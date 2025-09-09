#created by rarmada
#2025-09-09
#this will batch rename files in a directory 

import os 
from pathlib import Path
import shutil

def current_path() -> Path:
    return Path.cwd()

def createbackup(folderwork: Path):
    backup_path = folderwork / "backup"
    try:
        backup_path.mkdir(parents=True, exist_ok=True)
        print(f"Backup directory ready at: {backup_path}")
    except PermissionError:
        print(f"Permission denied: {backup_path}")
        return

    print("folder", folderwork)
    print("folder backup", backup_path)

    copyfiles(folderwork, backup_path)  # both are Path objects now
    
def copyfiles(src: Path, backup: Path):
    for item in src.iterdir():
        if item.name == backup.name and item.is_dir():
            continue  # skip backup itself
        target = backup / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)  # 3.8+
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
        
def batchrename(folderwork: Path):
    index = 0
    for fileX in folderwork.iterdir():
        if fileX.name == "backup" and fileX.is_dir():
            continue  # skip backup itself
        fileExt = os.path.splitext(fileX)[1]

        try:
            os.rename(fileX, os.path.join(os.path.dirname(fileX), f"{index}{fileExt}"))
        except Exception as e:
            print(f"Error renaming {fileX}: {e}")
        index += 1

       
        

def startprogram():
    print("Checking Directory:", current_path())
    optiondirectory = input("Enter directory path (or press Enter to use current directory): ").strip()
    if optiondirectory:
        os.chdir(optiondirectory) 
        print("Changed Directory to:", current_path())
    else:
        print("Using current directory:", current_path())
    
    #list folders
    base = Path(current_path())
    folders = [p for p in base.iterdir() if p.is_dir()] 
    print("Directory contents:")
    index = 0   
    for f in sorted(folders):        # sort by name (string order)
        print(f"[{index}] - {f}")
        index += 1
    if not folders:
        folderwork = current_path()
    else:
        option = input("Choose a folder number from the list above or type 'work' to use this directory: ").strip()
        if option.lower() == 'work':
            folderwork = current_path()            # Path
        else:
            idx = int(option)
            folderwork = folders[idx]              # Path
            # If you insist on changing the cwd:
            # os.chdir(folderwork)                 # DO NOT assign back to folderwork
    print("Selected folder:",  folderwork)
    optionbackup = input("Do you want to create a backup of this folder? (y/n): ").strip().lower()
    if optionbackup == 'y':
        print("Creating backup...")
        createbackup(folderwork)
        print("Backup created successfully.")
    else:
        print("Skipping backup.")
    batchrename(folderwork)


    

    #create backup of folder
    #batch rename files in folder
    
    













startprogram()