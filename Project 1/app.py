#created by rarmada
#2025-09-08
#this program will replace text in all .txt files in a directory /documents/1
import os 
#cwd = os.getcwd() 
#os.chdir('../') 
#os.chdir('/home/rarmada/Documents/Python/documents/1') 
def current_path():
    return os.getcwd()

def hasfiles(cname, cname2,option,dirlist):
    fileX = dirlist[option]
    if fileX.endswith(".txt"):
        try:
            # Read file
            with open(fileX, 'r') as f:
                filelines = f.readlines()

            # Replace content
            new_lines = [line.replace(cname, cname2) for line in filelines]

            # Write back changes
            with open(fileX, 'w') as f:
                f.writelines(new_lines)
            print("Changes made successfully in", fileX)
        except Exception as e:
            print(f"Error processing {fileX}: {e}")  
    else:
        print(f"Skipping non-txt file: {fileX}")
            
def startprogram():
    print("Checking for files in directory:", current_path())
    dirlist = os.listdir(current_path())
    print("Files found:")
    index = 0    
    for item in dirlist:
        print(f"[{index}] - {item}")
        index += 1

    print("choose a number from the list above or type 'exit' to quit:")
    option = input()
    if option.lower() == 'exit':
        print("Exiting program.")
        return
    option = int(option)
    print("Starting program...")
    print("this program will replace the name of the company in a .txt file in the directory of the project")
    cname = input("Choose name to search:").strip()
    cname2 = input("Choose name to replace:").strip()
    hasfiles(cname, cname2, option,dirlist)
    
startprogram()