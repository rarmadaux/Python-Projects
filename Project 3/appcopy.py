#created by rarmada
#2025-09-10
#this search and download files from sftp server
#require pip install paramiko
#require pip install python-dotenv

import os 
from pathlib import Path
import paramiko
from dotenv import load_dotenv
import posixpath, stat

def current_path() -> Path:
    return Path.cwd()

def createdownloadfolder():
    download_path = current_path() / "downloaded_files"
    try:
        download_path.mkdir(parents=True, exist_ok=True)
        print(f"Download directory ready at: {download_path}")
    except PermissionError:
        print(f"Permission denied: {download_path}")
        return None
    return download_path

def sftpconnect():
    load_dotenv(dotenv_path=Path(__file__).with_name(".env"))  # or Path.cwd() / ".env"

    hostname = os.getenv("SFTP_HOST")
    port = int(os.getenv("SFTP_PORT", "22"))
    username = os.getenv("SFTP_USER")
    password = os.getenv("SFTP_PASS")  # or KEY_PATH / KEY_PASSPHRASE


    SSH_Client = paramiko.SSHClient()
    SSH_Client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSH_Client.connect(hostname=hostname,
                    port=port,
                    username=username,
                    password=password,
                    look_for_keys=False)

    sftp_client = SSH_Client.open_sftp()
    print("Connection successfully established ... ")

    remoteFilePath = "/record/2025"
    # Output: lists of files ['my-directory', 'my-file']
    print(f"lists of files {sftp_client.listdir(remoteFilePath)}")
    return sftp_client

def createenv():
    env_path = current_path() / ".env"
    try:
        if not env_path.exists():
            with open(env_path, 'w') as f:
                host = input("Enter SFTP Host: ").strip()
                user = input("Enter SFTP User: ").strip()
                passwd = input("Enter SFTP Password: ").strip()
                port = input("Enter SFTP Port (default 22): ").strip() or "22"
                f.write(f"SFTP_HOST={host}\nSFTP_USER={user}\nSFTP_PASS={passwd}\nSFTP_PORT={port}\n")
            print(f".env file created at: {env_path}")
            try:
                os.chmod(env_path, 0o600)
            except Exception:
                pass  # skip on Windows

        else:
            print(f".env file already exists at: {env_path}")
    except PermissionError:
        print(f"Permission denied: {env_path}")
    return env_path

def searchfile():
    sftp = sftpconnect()
    try:
        search_term = input("Enter search term: ").strip().lower()
        root = "/record/2025"
        print(f"Searching under {root} for: {search_term!r}")

        # --- recursive walk over SFTP (Paramiko has no .walk) ---
        matches = []

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
        for remote_path in matches:
            local_path = download_dir / posixpath.basename(remote_path)
            try:
                sftp.get(remote_path, str(local_path))
                print(f"Downloaded {remote_path} -> {local_path}")
            except Exception as e:
                print(f"Error downloading {remote_path}: {e}")
    finally:
        try:
            sftp.close()
        except Exception:
            pass
       

def startprogram():
    createenv()
    searchfile()

startprogram()
