# created by rarmada
# 2025-09-10 (GUI version)
# SFTP search and download app with GUI
# pip install customtkinter paramiko python-dotenv
#python -m PyInstaller --onefile --noconsole --add-data ".env;." --icon icon.ico app2.py

import os
import posixpath
import stat
import threading
from pathlib import Path
import paramiko
from dotenv import load_dotenv
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

REMOTE_ROOT = "/record/2025"  # adjust as needed

# ---------- Utility ----------
def app_dir() -> Path:
    import sys
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent

def current_path() -> Path:
    return app_dir()

def createdownloadfolder() -> Path | None:
    download_path = current_path() / "downloaded_files"
    try:
        download_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        messagebox.showerror("Permission denied", f"Cannot create {download_path}")
        return None
    return download_path

# ---------- SFTP ----------
def sftpconnect():
    load_dotenv(dotenv_path=current_path() / ".env")
    hostname = os.getenv("SFTP_HOST")
    port = int(os.getenv("SFTP_PORT", "22"))
    username = os.getenv("SFTP_USER")
    password = os.getenv("SFTP_PASS")

    if not all([hostname, username, password]):
        raise RuntimeError("Missing credentials in .env file")

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=hostname, port=port, username=username, password=password, timeout=30)
    return ssh_client.open_sftp(), ssh_client

# ---------- GUI ----------
class SFTPApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SFTP File Searcher")
        self.geometry("700x500")

        self.sftp = None
        self.ssh = None

        # --- Connection Frame ---
        conn_frame = ctk.CTkFrame(self)
        conn_frame.pack(pady=10, padx=10, fill="x")

        self.host_entry = ctk.CTkEntry(conn_frame, placeholder_text="Host")
        self.user_entry = ctk.CTkEntry(conn_frame, placeholder_text="User")
        self.pass_entry = ctk.CTkEntry(conn_frame, placeholder_text="Password", show="*")
        self.port_entry = ctk.CTkEntry(conn_frame, placeholder_text="Port", width=80)
        self.connect_btn = ctk.CTkButton(conn_frame, text="Connect", command=self.connect_sftp)

        for w in (self.host_entry, self.user_entry, self.pass_entry, self.port_entry, self.connect_btn):
            w.pack(side="left", padx=5, pady=5)

        # --- Search Frame ---
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(padx=10, pady=(0, 10), fill="x")

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search term")
        self.search_btn = ctk.CTkButton(search_frame, text="Search", command=self.search_files)

        self.search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.search_btn.pack(side="left", padx=5)

        # --- Results Frame ---
        self.results_frame = ctk.CTkScrollableFrame(self, label_text="Results")
        self.results_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Load saved credentials
        self.load_env()
        # Auto-connect if credentials exist
        if all([self.host_entry.get(), self.user_entry.get(), self.pass_entry.get()]):
            threading.Thread(target=self.connect_sftp, daemon=True).start()

    # ---------- Methods ----------
    def load_env(self):
        env = current_path() / ".env"
        if env.exists():
            load_dotenv(env)
            self.host_entry.insert(0, os.getenv("SFTP_HOST", ""))
            self.user_entry.insert(0, os.getenv("SFTP_USER", ""))
            self.pass_entry.insert(0, os.getenv("SFTP_PASS", ""))
            self.port_entry.insert(0, os.getenv("SFTP_PORT", "22"))

    def save_env(self):
        env_path = current_path() / ".env"
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(
                f"SFTP_HOST={self.host_entry.get().strip()}\n"
                f"SFTP_USER={self.user_entry.get().strip()}\n"
                f"SFTP_PASS={self.pass_entry.get().strip()}\n"
                f"SFTP_PORT={self.port_entry.get().strip() or '22'}\n"
            )

    def connect_sftp(self):
        try:
            self.save_env()
            self.sftp, self.ssh = sftpconnect()
            messagebox.showinfo("Connection", "Connected successfully!")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def search_files(self):
        if not self.sftp:
            messagebox.showwarning("Not connected", "Please connect to the SFTP first.")
            return

        term = self.search_entry.get().strip().lower()
        if not term:
            messagebox.showwarning("Missing term", "Enter a search term.")
            return

        # Clear old results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        threading.Thread(target=self._search_thread, args=(term,), daemon=True).start()

    def _search_thread(self, term):
        matches = []

        def walk(dirpath):
            for entry in self.sftp.listdir_attr(dirpath):
                path = posixpath.join(dirpath, entry.filename)
                if stat.S_ISDIR(entry.st_mode):
                    walk(path)
                elif term in entry.filename.lower():
                    matches.append({
                        "path": path,
                        "size": entry.st_size,
                        "mtime": entry.st_mtime
                    })

        try:
            walk(REMOTE_ROOT)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Search Error", str(e)))
            return

        if not matches:
            self.after(0, lambda: messagebox.showinfo("No results", "No matching files found."))
            return

        self.after(0, lambda: self.display_results(matches))

    def display_results(self, matches):
        for file in matches:
            path = file["path"]
            size = file["size"]
            mtime = file["mtime"]

            size_mb = size / (1024 * 1024)
            date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

            frame = ctk.CTkFrame(self.results_frame)
            frame.pack(fill="x", padx=5, pady=2)

            info = f"{path}   [{size_mb:.1f} MB | {date_str}]"
            label = ctk.CTkLabel(frame, text=info, anchor="w")
            label.pack(side="left", padx=5, pady=5, fill="x", expand=True)

            btn = ctk.CTkButton(frame, text="Download", width=100,
                                command=lambda p=path: threading.Thread(target=self.download_file, args=(p,), daemon=True).start())
            btn.pack(side="right", padx=5)

    def download_file(self, remote_path):
        download_dir = createdownloadfolder()
        if not download_dir:
            return

        local_path = download_dir / posixpath.basename(remote_path)
        try:
            self.sftp.get(remote_path, str(local_path))
            messagebox.showinfo("Download complete", f"Downloaded:\n{local_path}")
        except Exception as e:
            messagebox.showerror("Download failed", str(e))

    def on_close(self):
        try:
            if self.sftp:
                self.sftp.close()
            if self.ssh:
                self.ssh.close()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = SFTPApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
