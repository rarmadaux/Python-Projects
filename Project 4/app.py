# created by rarmada
# 2025-09-10
# this searches and downloads files from an SFTP server
# require: pip install paramiko python-dotenv

import os
import sys
import shutil
from pathlib import Path
import paramiko        # <-- you need this
from dotenv import load_dotenv

REMOTE_ROOT = "/"      # <-- or set your actual remote root folder

def current_path() -> Path:
    return Path.cwd()


def createFolders() -> Path | None:
    upload_path = current_path() / "upload folder"
    try:
        upload_path.mkdir(parents=True, exist_ok=True)
        print(f"Download directory ready at: {upload_path}")
    except PermissionError:
        print(f"Permission denied: {upload_path}")
        return None
    
    download_path = current_path() / "upload folder"
    try:
        download_path.mkdir(parents=True, exist_ok=True)
        print(f"Download directory ready at: {download_path}")
    except PermissionError:
        print(f"Permission denied: {download_path}")
        return None
    
    return upload_path, download_path

def run_remote_command(ssh_client, command: str):
    """Run a command on the remote server and return stdout + stderr"""
    stdin, stdout, stderr = ssh_client.exec_command(command)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return out, err

def menu(page: int = 1) -> str:
    border = "+" + "-"*50 + "+"
    title = ""
    options = []

    match page:
        case 1:  # Main menu
            title = "|       🛠️  Minecraft Server Manager 🛠️       |"
            options = [
                "0. First time configuration ( reset all config )",
                "1. PC configuration ",
                "2. Machine configuration (update / ...)",
                "3. Minecraft Server configuration (start/stop/restart/backup)",
                "4. Exit"
            ]
        case 2:  # Machine configuration
            title = "|           ⚙️  Machine Configuration ⚙️        |"
            options = [
                "0. Update environment variables (.env)",
                "1. Update OS / Install dependencies",
                "2. Create Minecraft user & permissions",
                "3. Delete Minecraft user & permissions",
                "4. Install / Choose java version",
                "5. Back to Main Menu",
                "6. Exit"
            ]
        case 3:  # Server configuration
            title = "|           🎮  Server Configuration 🎮         |"
            options = [
                "1. Start Server",
                "2. Stop Server",
                "3. Restart Server",
                "4. Backup Server",
                "5. Back to Main Menu",
                "6. Exit"
            ]
        case 4:  #  First time configuration
            title = "|           🎮  Frist Configuration 🎮         |"
            options = [
                "1. Connect to server",
                "2. Create User for Minecraft",
                "3. Back to Main Menu",
                "4. Exit"
            ]
        case _:
            print("Invalid menu page.")
            sys.exit(1)

    print(border)
    print(title)
    print(border)
    for opt in options:
        print(f"| {opt:<48} |")
    print(border)

    choice = input("Enter your choice: ")
    return choice

def sshconnect_interactive():
    
    load_dotenv(dotenv_path=current_path() / ".env")  # still use hostname/port from .env

    hostname = os.getenv("SFTP_HOST")
    port = int(os.getenv("SFTP_PORT", "22"))

    if not hostname:
        raise RuntimeError("Missing SFTP_HOST in .env")

    username = input("Enter root username: ").strip()
    password = input("Enter root password: ").strip()

    if not username or not password:
        raise RuntimeError("Username and password are required.")

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
    print(f"Connection successfully established as {username} ...")

    return sftp_client, ssh_client

def sshconnect():
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
    run_remote_command(ssh_client, "ls -la")
    # Example probe (can be removed if noisy)
    #try:
    #    print(f"lists of files {sftp_client.listdir(REMOTE_ROOT)}")
    #except Exception:
    #    pass

    return sftp_client, ssh_client

def createuserserver():
    
    load_dotenv(dotenv_path=current_path() / ".env")  # still use hostname/port from .env

    hostname = os.getenv("SFTP_HOST")
    port = int(os.getenv("SFTP_PORT", "22"))

    if not hostname:
        raise RuntimeError("Missing SFTP_HOST in .env")

    username = input("Enter root username: ").strip()
    password = input("Enter root password: ").strip()

    if not username or not password:
        raise RuntimeError("Username and password are required.")

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        look_for_keys=False,
        timeout=30
    )

    sftp_client = ssh_client.open_sftp()
    print(f"Connection successfully established as {username} ...")

    return sftp_client, ssh_client


def createenv(update: bool = False) -> Path:
    env_path = current_path() / ".env"
    
    if env_path.exists() and not update:
        print(f".env file already exists at: {env_path}")
        return env_path
    
    # Read existing values if updating
    env_data = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env_data[key] = value
    
    # Ask for each variable, use existing as default if updating
    host = input(f"Enter SFTP Host [{env_data.get('SFTP_HOST','')}]: ").strip() or env_data.get("SFTP_HOST","")
    user = input(f"Enter SFTP User [{env_data.get('SFTP_USER','')}]: ").strip() or env_data.get("SFTP_USER","")
    passwd = input(f"Enter SFTP Password [{env_data.get('SFTP_PASS','')}]: ").strip() or env_data.get("SFTP_PASS","")
    port = input(f"Enter SFTP Port [{env_data.get('SFTP_PORT','22')}]: ").strip() or env_data.get("SFTP_PORT","22")
    
    # Write new values
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"SFTP_HOST={host}\n")
        f.write(f"SFTP_USER={user}\n")
        f.write(f"SFTP_PASS={passwd}\n")
        f.write(f"SFTP_PORT={port}\n")
    
    print(f"✅ .env file updated at: {env_path}")
    try:
        os.chmod(env_path, 0o600)
    except Exception:
        pass
    
    return env_path


def updateserver():
    
    sftp_client, ssh_client = sshconnect()
    print("🔄 Updating server...")
    command = "sudo apt update && sudo apt upgrade -y"
    stdin, stdout, stderr = ssh_client.exec_command(command, get_pty=True)

    # Optional: send sudo password if needed
    root_pass = input("Enter root password to perform system updates: ").strip()

    stdin.write(root_pass + "\n")
    stdin.flush()

    # Read output line by line
    for line in iter(stdout.readline, ""):
        print(line, end="")  # print as it comes

    # Read errors too
    err_output = stderr.read().decode()
    if err_output:
        print("\nErrors:\n", err_output)

    # Wait for exit status
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print("\n✅ Server update completed successfully.")
    else:
        print("\n❌ Server update failed!")

    sftp_client.close()
    ssh_client.close()

def createuserserver():
    sftp_client, ssh_client = sshconnect()
    print("👤 Creating Minecraft user...")
    
    mc_user = input("Enter Minecraft username to create: ").strip()
    if not mc_user:
        print("Invalid username.")
        return
    
    password = input("Enter root password  ")

    commands = [
        f"sudo adduser --disabled-password --gecos '' {mc_user}",
        f"sudo mkdir -p /opt/minecraft",
        f"sudo chown {mc_user}:{mc_user} /opt/minecraft",
        f"sudo chmod 750 /opt/minecraft"
    ]

    for cmd in commands:
        stdin, stdout, stderr = ssh_client.exec_command(cmd, get_pty=True)
        
        stdin.write(password + "\n")
        stdin.flush()

        for line in iter(stdout.readline, ""):
            print(line, end="")

        err_output = stderr.read().decode()
        if err_output:
            print("\nErrors:\n", err_output)

        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print(f"\n✅ Command succeeded: {cmd}")
        else:
            print(f"\n❌ Command failed: {cmd}")

    sftp_client.close()
    ssh_client.close()

    update_env_user(mc_user)

def update_env_user(new_user: str):
    env_path = current_path() / ".env"
    if not env_path.exists():
        print(".env file not found!")
        return
    lines = []
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("SFTP_USER="):
                lines.append(f"SFTP_USER={new_user}\n")
            else:
                lines.append(line)
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"✅ Updated SFTP_USER to {new_user} in .env")

def delete_minecraft_user(ssh_client, username: str, root_password: str):
    
    # Command to delete the user and their home folder
    command = f"sudo -S deluser --remove-home {username}"
    
    stdin, stdout, stderr = ssh_client.exec_command(command, get_pty=True)
    
    # Send sudo password
    stdin.write(root_password + "\n")
    stdin.flush()
    
    # Read stdout in real-time
    for line in iter(stdout.readline, ""):
        print(line, end="")
    
    # Check for errors
    err_output = stderr.read().decode()
    if err_output:
        print("\nErrors:\n", err_output)
    
    # Check exit status
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"\n✅ User '{username}' deleted successfully.")
    else:
        print(f"\n❌ Failed to delete user '{username}'!")

def delete_user_menu():
    # Connect with the original SFTP/root user
    sftp_client, ssh_client = sshconnect_interactive()
    
    mc_user = input("Enter Minecraft username to delete: ").strip()
    if not mc_user:
        print("Invalid username.")
        return
    
    root_pass = input("Enter root password to delete user: ").strip()
    
    delete_minecraft_user(ssh_client, mc_user, root_pass)
    
    sftp_client.close()
    ssh_client.close()

def choose_or_install_java():
    sftp_client, ssh_client = sshconnect_interactive()
    print("☕ Java Setup for Minecraft Server")

    root_pass = input("Enter root password: ").strip()

    # Step 1: List installed Java versions
    cmd_installed = "update-alternatives --list java || true"
    stdin, stdout, stderr = ssh_client.exec_command(cmd_installed, get_pty=True)
    #stdin.write(root_pass + "\n")
    stdin.flush()
    installed_versions = stdout.read().decode().splitlines()

    if installed_versions:
        print("\nInstalled Java versions:")
        for i, v in enumerate(installed_versions, 1):
            print(f"{i}. {v}")
        choice = input("Select a version to activate (or press Enter to isntall new): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(installed_versions):
            selected = installed_versions[int(choice)-1]
            print(f"Setting {selected} as active Java version...")
            cmd_set = f"sudo update-alternatives --set java {selected}"
            stdin, stdout, stderr = ssh_client.exec_command(cmd_set, get_pty=True)
            stdin.write(root_pass + "\n")
            stdin.flush()
            for line in iter(stdout.readline, ""):
                print(line, end="")
            stdout.channel.recv_exit_status()
    else:
        print("No Java versions currently installed.")

    # Step 2: Ask if user wants to install a new version
    install_new = input("Do you want to install a new Java version? (y/n): ").strip().lower()
    if install_new == "y":
        cmd_available = "apt-cache search openjdk | awk '{print $1}' | grep -E 'openjdk-(8|11|17|21)-(jdk|jre)$'"
        stdin, stdout, stderr = ssh_client.exec_command(cmd_available, get_pty=True)
        stdin.write(root_pass + "\n")
        stdin.flush()
        available_versions = stdout.read().decode().splitlines()

        if not available_versions:
            print("No suitable Java versions found.")
        else:
            print("\nAvailable Java versions to install:")
            for i, pkg in enumerate(available_versions, 1):
                print(f"{i}. {pkg}")
            choice = input("Select a version to install (or Enter for default-jdk): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(available_versions):
                java_version = available_versions[int(choice)-1]
            else:
                java_version = "default-jdk"

            print(f"Installing {java_version}...")
            cmd_install = f"sudo apt update && sudo apt install -y {java_version}"
            stdin, stdout, stderr = ssh_client.exec_command(cmd_install, get_pty=True)
            stdin.write(root_pass + "\n")
            stdin.flush()
            for line in iter(stdout.readline, ""):
                print(line, end="")
            stdout.channel.recv_exit_status()
            print(f"\n✅ Java ({java_version}) installed.")

    sftp_client.close()
    ssh_client.close()


def program():
    optionmenu = menu()

    match optionmenu:
        case "0":
            # First time configuration
            
            optionmenu = menu(4)
            match optionmenu:
                case "1":
                    print("Conencting to server..")
                    createenv()
                    returnupd = updateserver()
                    menu(4)

                case "2":
                    print("Creating Minecraft user and setting permissions...")
                    createuserserver()
                    menu(4)

                case "3": optionmenu = menu()
                case "4":
                    print("Exiting program.")
                    sys.exit(0)
                case _:
                    print("Invalid choice.")
                    menu(2)

            
            
        case "1": #pc server configuration
            optionmenu = menu(2)
            match optionmenu:
                case "0":
                    print("Updating .env file...")
                    createenv(update=True)
                case "1":
                    print("Updating server OS and dependencies...")
                    updateserver()
                    menu(2)
                case "2":
                    print("Creating Minecraft user and setting permissions...")
                    createuserserver()
                    menu(2)

                case "3":
                    print("Deleting Minecraft user and setting permissions...")
                    delete_user_menu()
                    menu(2)

                case "4":
                    print("Install java")
                    choose_or_install_java()
                    menu(2)
                case "5":
                    print("Exiting program.")
                    menu(1)
                case _:
                    print("Invalid choice.")
                    menu(1)
        case "3":
            print("Server configuration...")
        case "6":
            print("Exiting program.")
            sys.exit(0)
        case _:
            print("Invalid choice. Exiting.")
            sys.exit(1)
    

program()