# created by rarmada
# 2025-09-10
# this searches and downloads files from an SFTP server
# require: pip install paramiko python-dotenv

import os
import sys
from pathlib import Path
import posixpath
import stat
import paramiko
from dotenv import load_dotenv

REMOTE_ROOT = "/record/2025"  # adjust as needed

def app_dir() -> Path:
    """Folder where the app lives (works for PyInstaller and normal runs)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent

def current_path() -> Path:
    return app_dir()

def createdownloadfolder() -> Path | None:
    download_path = current_path() / "downloaded_files"
    try:
        download_path.mkdir(parents=True, exist_ok=True)
        print(f"Download directory ready at: {download_path}")
    except PermissionError:
        print(f"Permission denied: {download_path}")
        return None
    return download_path

def sftpconnect():
    # Load .env from app folder (next to EXE/script)
    load_dotenv(dotenv_path=current_path() / ".env")

    hostname = os.getenv("SFTP_HOST")
    port = int(os.getenv("SFTP_PORT", "22"))
    username = os.getenv("SFTP_USER")
    password = os.getenv("SFTP_PASS")  # or KEY_PATH / KEY_PASSPHRASE

    if not all([hostname, username, password]):
        raise RuntimeError("Missing SFTP credentials in .env (SFTP_HOST, SFTP_USER, SFTP_PASS).")

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        look_for_keys=False,
        timeout=30,
    )

    sftp_client = ssh_client.open_sftp()
    print("Connection successfully established ... ")
    # Example probe (can be removed if noisy)
    try:
        print(f"lists of files {sftp_client.listdir(REMOTE_ROOT)}")
    except Exception:
        pass

    return sftp_client, ssh_client

def createenv() -> Path:
    env_path = current_path() / ".env"
    try:
        if not env_path.exists():
            with open(env_path, 'w', encoding='utf-8') as f:
                host = input("Enter SFTP Host: ").strip()
                user = input("Enter SFTP User: ").strip()
                passwd = input("Enter SFTP Password: ").strip()
                port = input("Enter SFTP Port (default 22): ").strip() or "22"
                f.write(
                    f"SFTP_HOST={host}\n"
                    f"SFTP_USER={user}\n"
                    f"SFTP_PASS={passwd}\n"
                    f"SFTP_PORT={port}\n"
                )
            print(f".env file created at: {env_path}")
            try:
                os.chmod(env_path, 0o600)
            except Exception:
                # Windows may not support POSIX perms; ignore
                pass
        else:
            print(f".env file already exists at: {env_path}")
    except PermissionError:
        print(f"Permission denied: {env_path}")
    return env_path

def searchfile():
    sftp = ssh = None
    try:
        sftp, ssh = sftpconnect()

        search_term = input("Enter search term: ").strip().lower()
        root = REMOTE_ROOT
        print(f"Searching under {root} for: {search_term!r}")

        matches: list[str] = []

        def walk(dirpath: str):
            for entry in sftp.listdir_attr(dirpath):
                path = posixpath.join(dirpath, entry.filename)
                if stat.S_ISDIR(entry.st_mode):
                    walk(path)  # recurse into subdir
                else:
                    if search_term in entry.filename.lower():
                        matches.append(path)

        walk(root)

        if not matches:
            print("No matching files found.")
            return

        print("Found matches:")
        for i, p in enumerate(matches, 1):
            print(f"[{i}] {p}")

        if input("Type 'y' to download all found files, or 'n' to skip: ").strip().lower() != "y":
            print("No files downloaded.")
            return

        download_dir = createdownloadfolder()
        if not download_dir:
            print("Cannot create download directory. Aborting downloads.")
            return

        for remote_path in matches:
            local_path = download_dir / posixpath.basename(remote_path)
            try:
                sftp.get(remote_path, str(local_path))
                print(f"Downloaded {remote_path} -> {local_path}")
            except Exception as e:
                print(f"Error downloading {remote_path}: {e}")

    finally:
        try:
            if sftp:
                sftp.close()
        except Exception:
            pass
        try:
            if ssh:
                ssh.close()
        except Exception:
            pass

def startprogram():
    createenv()
    searchfile()

if __name__ == "__main__":
    startprogram()
