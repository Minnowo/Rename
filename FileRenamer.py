import os 
import datetime
from contextlib import contextmanager
import time
import re
import random

crtdate_rename = False
mdfdate_rename = False

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''alist.sort(key=natural_keys) sorts in human order http://nedbatchelder.com/blog/200712/human_sorting.html    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


def file_only_blacklist():
    list = [i.strip() for i in input("\nInput the names of files you would like to blacklist seperated by \" / \"(ex a.txt / b.png)\n").split("/") if i.strip() != ""]
    return list, []
    print(list)

def filetype_only_blacklist():
    list = [i.strip() for i in input("\nInput the names of filetypes you would like to blacklist seperated by \" / \" (ex .txt / .png)\n").split("/") if i.strip() != ""]
    print(list)
    return [], list

def file_filetype_blacklist():
    return file_only_blacklist()[0], filetype_only_blacklist()[1]

def rename_date_created(dir, file, new_name):
    file = "\\".join([dir, file])
    new_name = "\\".join([dir, str(datetime.datetime.fromtimestamp(os.stat(file).st_ctime).strftime('%Y-%m-%d')) + "_" + new_name.split("_")[-1]])
    return file, new_name
    print(file)

def rename_date_modified(dir, file, new_name):
    file = "\\".join([dir, file])
    new_name = "\\".join([dir, str(datetime.datetime.fromtimestamp(os.stat(file).st_mtime).strftime('%Y-%m-%d')) + "_" + new_name.split("_")[-1]])
    return file, new_name
    print(file)

def rename_as_provided(dir, file, new_name):
    file = "\\".join([dir, file])
    new_name = "\\".join([dir, new_name])
    return file, new_name
    print(file)
    print(new_name)

rename_functins = {"%d%" : rename_date_created, "%m%" : rename_date_modified}
blacklist_functions = {1 : file_only_blacklist, 2 : filetype_only_blacklist, 3 : file_filetype_blacklist}



#***************** get the path to file folder sort by modified time *************. 
while True:
    directory_path = input("Paste path to file\n")

    if os.path.exists(directory_path):
        with cd(directory_path):
            files = filter(os.path.isfile, os.listdir(directory_path))
            files = list(files)
            files.sort(key= natural_keys)
        break
    else:
        print("\nPath does not exist\n")


#***************** display a small view of whats in the file folder *************. 
print("\nFolder preview:")
for index in range(0, len(files)):
    if index == 3:
        print("\t", "{}".format(files[index]))
        print("\t",len(files) - 4, "more files\n")
        break
    else:
        if files[index] == files[-1]:
            print("\t", "{}\n".format(files[index]))
        else:
            print("\t", files[index])

#***************** ask if there are any files they do not want to rename *************. 

try:
    blacklist = int(input("\nWould you like to blacklist any files or filetypes? \n\t0 : None\n\t1 : Files\n\t2 : Filetype\n\t3 : Both\n"))
    blacklist = blacklist_functions.get(blacklist, [])
    blacklists = {"files" : [], "file types" : []}

    if blacklist != []: 
        blacklists["files"], blacklists["file types"] = blacklist() 
except:
    blacklists = {"files" : [], "file types" : []}

print("\nBlacklists: ", blacklists, "\n")
rename_as = input("Raname all as? (%d% to raname as date created, %m% to rename as date modified)\n")


#***************** main loop *************. 
offset = 0
rename_count = 0
start = time.perf_counter()

for file in files:
    file_type = f".{file.split('.')[-1]}"

    if file_type in blacklists["file types"] or file in blacklists["files"]:
        print(f"{file} was blacklisted") 
    else:
        output = rename_functins.get(rename_as, rename_as_provided)
        while True:
            try:
                old_name, new_name = output(directory_path, file, f"{rename_as}_{offset}{file_type}")
                if old_name == new_name: 
                    offset += 1
                    break
                else:
                    os.rename(old_name, new_name)
                    offset += 1
                    rename_count += 1
                    print(f"Renaming {old_name}",f"as --> {new_name}")
                break
            except FileExistsError:                         # if file already exists generate a temp name for that file and rename it
                print("file exists renaming it")
                files.remove(new_name.split("\\")[-1])
                temp_name = str(random.randint(999, 99999)) + file_type 
                while temp_name in files:
                    temp_name = str(random.randint(0, 99999)) + file_type 
                os.rename(new_name, directory_path + "\\" + temp_name)
                files.append(temp_name)     
                rename_count -= 1
            except Exception as e:
                print(e)
                rename_count -= 1
                break

        

if rename_count <= 0:
    print("\nNothing has been renamed")
else:
    print('\nRenamed {} files as {}_x'.format(rename_count, rename_as))

finished = time.perf_counter()
print(f"Finished in {round(finished - start, 5)} seconds")
input('Press exit or enter to close')