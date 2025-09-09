#created by rarmada
#2025-09-08
#this program will replace text in all .txt files in a directory /documents/1
import os 
cwd = os.getcwd() 
os.chdir('../') 
os.chdir('/home/rarmada/Documents/Python/documents/1') 
def current_path():
    return os.getcwd()
dirlist = os.listdir(current_path())

def hasfiles(cname, cname2):
    for fileX in dirlist:
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

                print(f"Updated: {fileX}")

            except Exception as e:
                print(f"Error processing {fileX}: {e}")  

def startprogram():
    print("Starting program...")
    print("this program will replace the name of the company in all .txt files in the directory documents/1")
    if dirlist:
        print("Choose name to search:")
        cname = input()
        print("Choose name to replace:")
        cname2 = input()
        hasfiles(cname, cname2)
        
    else:
        print("The directory is empty")



startprogram()