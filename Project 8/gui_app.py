import os
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess, threading, platform, queue, psutil

CONFIG_FILE = os.path.join("config", "apps.json")
APP_PATH = os.path.abspath("app.py")


class PCControllerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PC Controller - Host")
        self.geometry("900x550")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.server_process = None
        self.os_name = platform.system().lower()

        # Tabs
        self.tabview = ctk.CTkTabview(self, width=800, height=500)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.apps_tab = self.tabview.add("⚙️ Apps")
        self.server_tab = self.tabview.add("🖥️ Server")
        self.settings_tab = self.tabview.add("⚡ Settings")

        # --- APPS TAB ---
        self.apps_tab.grid_columnconfigure(0, weight=1)
        self.apps_tab.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self.apps_tab,
            text="Configured Applications",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, pady=(10, 5))

        # Buttons Row
        btn_frame = ctk.CTkFrame(self.apps_tab)
        btn_frame.grid(row=1, column=0, pady=5)
        ctk.CTkButton(btn_frame, text="➕ Add App", command=self.add_app, width=120).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_frame, text="💾 Save Config", command=self.save_config, width=120).grid(row=0, column=1, padx=10)

        # Start/Stop button
        self.server_btn = ctk.CTkButton(btn_frame, text="▶ Start Server", command=self.start_server, width=150)
        self.server_btn.grid(row=0, column=2, padx=10)

        # Scrollable App List
        self.app_frame = ctk.CTkScrollableFrame(self.apps_tab, height=350, label_text="App List")
        self.app_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        # --- SERVER TAB ---
        self.log_box = ctk.CTkTextbox(self.server_tab, height=400, width=760)
        self.log_box.pack(padx=20, pady=20, fill="both", expand=True)
        self.log_box.insert("end", "Server logs will appear here...\n")

        # --- SETTINGS TAB ---
        ctk.CTkLabel(self.settings_tab, text="Future Settings Here", font=ctk.CTkFont(size=16)).pack(pady=30)

        # Load Apps
        self.load_config()
        # Detect existing Flask
        self.check_existing_server()

    # --- App Config Management ---
    def load_config(self):
        for widget in self.app_frame.winfo_children():
            widget.destroy()

        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                apps = json.load(f)
        else:
            apps = {}

        if not apps:
            ctk.CTkLabel(
                self.app_frame,
                text="No apps configured yet. Click 'Add App'.",
                text_color="gray"
            ).grid(row=0, column=0, pady=10)
            return

        for i, (name, path) in enumerate(apps.items()):
            row = ctk.CTkFrame(self.app_frame)
            row.grid(row=i, column=0, sticky="ew", pady=5, padx=5)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=name, width=120, anchor="w",
                         font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w", padx=10)

            display_path = path if len(path) < 80 else "..." + path[-77:]
            ctk.CTkLabel(row, text=display_path, anchor="w", text_color="#aaa").grid(row=0, column=1, sticky="w", padx=10)

            ctk.CTkButton(row, text="❌", width=40, fg_color="#8b0000",
                          hover_color="#a50000", command=lambda n=name: self.remove_app(n)).grid(row=0, column=2, padx=10)

    def add_app(self):
        file_path = filedialog.askopenfilename(
            title="Select Application",
            filetypes=[("Executable files", "*.exe")] if self.os_name == "windows" else [("All Files", "*.*")]
        )
        if not file_path:
            return
        name = os.path.splitext(os.path.basename(file_path))[0].lower()
        current = self.get_apps()
        current[name] = file_path
        self.save_to_file(current)
        self.load_config()

    def remove_app(self, name):
        data = self.get_apps()
        if name in data:
            del data[name]
            self.save_to_file(data)
            self.load_config()

    def save_config(self):
        messagebox.showinfo("Saved", "Configuration saved successfully!")

    def get_apps(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_to_file(self, data):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

    # --- Server Control ---
    def start_server(self):
        if self.is_server_running():
            messagebox.showinfo("Server", "Server is already running!")
            return

        self.log_box.insert("end", "\n🚀 Starting server...\n")
        self.log_box.see("end")
        self.log_queue = queue.Queue()

        threading.Thread(target=self.run_flask_background, daemon=True).start()
        self.after(100, self.poll_log_queue)
        self.after(500, self.update_server_button)

    def stop_server(self):
        if not self.is_server_running():
            messagebox.showinfo("Server", "No server is currently running.")
            return

        self.log_box.insert("end", "\n🛑 Stopping server...\n")
        try:
            if hasattr(self.server_process, "terminate"):
                self.server_process.terminate()
            else:
                self.server_process.kill()
        except Exception as e:
            self.log_box.insert("end", f"⚠️ Error stopping server: {e}\n")

        self.server_process = None
        self.update_server_button()
        self.log_box.insert("end", "✅ Server stopped.\n")

    def update_server_button(self):
        if hasattr(self, "server_btn"):
            self.server_btn.destroy()

        parent = self.apps_tab.winfo_children()[1]

        if self.is_server_running():
            self.server_btn = ctk.CTkButton(
                parent, text="🛑 Stop Server",
                command=self.stop_server, width=150,
                fg_color="#8b0000", hover_color="#a50000"
            )
        else:
            self.server_btn = ctk.CTkButton(
                parent, text="▶ Start Server",
                command=self.start_server, width=150,
                fg_color="#1f6aa5"
            )
        self.server_btn.grid(row=0, column=2, padx=10, pady=5)

    def run_flask_background(self):
        try:
            flags = subprocess.CREATE_NO_WINDOW if platform.system().lower() == "windows" else 0
            self.server_process = subprocess.Popen(
                ["python", "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=flags
            )
            for line in iter(self.server_process.stdout.readline, ''):
                if not line:
                    break
                self.log_queue.put(line)
        except Exception as e:
            self.log_queue.put(f"❌ Error: {e}\n")

    def poll_log_queue(self):
        try:
            while not self.log_queue.empty():
                line = self.log_queue.get_nowait()
                self.log_box.insert("end", line)
                self.log_box.see("end")
        except Exception:
            pass

        if self.is_server_running():
            self.after(100, self.poll_log_queue)
        else:
            self.log_box.insert("end", "\n⚠️ Server stopped.\n")
            self.update_server_button()

    def on_close(self):
        if self.is_server_running():
            try:
                self.log_box.insert("end", "\n🛑 Stopping server before exit...\n")
                if hasattr(self.server_process, "terminate"):
                    self.server_process.terminate()
                else:
                    self.server_process.kill()
            except Exception:
                pass
        self.destroy()

    def check_existing_server(self):
        """Detect Flask/app.py processes belonging to this project"""
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = proc.info.get("cmdline") or []
                if not isinstance(cmdline, (list, tuple)):
                    continue  # Skip weird cases

                cmd = " ".join(cmdline).lower()
                if (
                    "python" in cmd
                    and "app.py" in cmd
                    and os.path.dirname(APP_PATH).lower() in cmd
                ):
                    self.log_box.insert("end", f"\n⚠️ Found running server (PID: {proc.pid})\n")
                    self.server_process = psutil.Process(proc.pid)
                    self.update_server_button()
                    return
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        self.update_server_button()

    def is_server_running(self):
        if not self.server_process:
            return False

        if hasattr(self.server_process, "poll"):
            return self.server_process.poll() is None

        if isinstance(self.server_process, psutil.Process):
            try:
                return self.server_process.is_running() and self.server_process.status() != psutil.STATUS_ZOMBIE
            except psutil.NoSuchProcess:
                return False
        return False


if __name__ == "__main__":
    app = PCControllerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
