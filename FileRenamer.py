
import os 
import datetime
from contextlib import contextmanager
import time


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


#***************** get the path to file folder sort by modified time *************. 
while True:
    InputFile = input("Paste path to file\n")
    search = InputFile
    try:
        with cd(search):
            #os.chdir(search)
            files = filter(os.path.isfile, os.listdir(search))
            files = list(files)
            files.sort(key=lambda x: os.path.getmtime(x))
            search = files
        break
    except:
        print("path not found \n")


#***************** display a small view of whats in the file folder *************. 
if len(search) > 3:
    #print('\n')
    for i in range(0,3 ):
        print(search[i])
        if i == 2:
            print("ect... \n")
elif len(search) != 0:
    #print('\n')
    for i in range(0, len(search)):
        print(search[i])
        if i ==  len(search):
            print("ect... \n")


#***************** ask if they want to rename by date created instead of choosing a name *************. 
rename_by_crtdate = ""
while rename_by_crtdate != "y" or rename_by_crtdate != "n":
    rename_by_crtdate = input("would you like to rename the files using the date created? y/n \n")
    if rename_by_crtdate == "y" or rename_by_crtdate == "n":
        break
if rename_by_crtdate == "y":
    while True:
        mdfdate = input("If these files were copied the creation date may have been changed, would you like to use the Last Modified time instead? y/n \n")
        if mdfdate == "y" or mdfdate == "n": break
    if mdfdate == "y":
        mdfdate_rename = True
        crtdate_rename = True
    else:
        crtdate_rename = True
        mdfdate_rename = False
    RenameName = ""
else:
    RenameName = input('Rename all as?\n')
    crtdate_rename = False


#***************** ask if there are any files they do not want to rename *************. 
BlacklistAsk = input("If you would like to blacklist any files, type the filename seperated by \" $$$ \" (ex text.txt $$$ text2.txt $$$ cat.png)\n")
if BlacklistAsk.find(" $$$ ") > 0:
    Blacklist = BlacklistAsk.split(" $$$ ")
    Blacklist = [x.strip(' ') for x in Blacklist]
else:
    if len(BlacklistAsk) != 0:
        Blacklist = []
        Blacklist.append(BlacklistAsk.strip(' '))
    else:
        Blacklist = []

#***************** ask if there are any files types do not want to rename *************. 
BlacklistAsk1 = input("If you would like to blacklist any file types, type the filetype seperated by \" $$$ \" (ex .txt $$$ .png $$$ .jpg)\n")
if BlacklistAsk1.find(" $$$ ") > 0:
    Blacklistfile = BlacklistAsk1.split(" $$$ ")
    Blacklistfile = [x.strip(' ') for x in Blacklistfile]
else:
    if len(BlacklistAsk1) != 0:
        Blacklistfile = []
        Blacklistfile.append(BlacklistAsk1.strip(' '))
    else:
        Blacklistfile = []

#print(Blacklistfile)
#***************** main loop *************. 
Number = 0
Count = 0
FiletypeCount = 0
check_for_datechange = []
check_for_datechange.append('')
start = time.perf_counter()
for img in search:
    filetype = "." + str(img).split(".")[-1:][0] # Grab the file type
    if filetype not in Blacklistfile:
        if img not in Blacklist:
            try:
                if crtdate_rename == True:
                    if mdfdate_rename == True:
                        created= os.stat("{}\\{}".format(InputFile, img)).st_mtime
                    else:
                        created= os.stat("{}\\{}".format(InputFile, img)).st_ctime
                    timestamp = datetime.datetime.fromtimestamp(created)
                    RenameName = timestamp.strftime('%Y-%m-%d')
                    check_for_datechange.append(RenameName)
                    if len(check_for_datechange) > 2:
                        check_for_datechange.pop(0)
                    if str(check_for_datechange[0]) != str(RenameName):
                        Number = 0
                try:
                    os.rename("{}\\{}".format(InputFile, img), "{}\\{}_{}{}".format(InputFile, RenameName, Number, filetype))
                    print("Renaming {}\\{}".format(InputFile, img),"as --> {}\\{}_{}{}".format(InputFile, RenameName, Number, filetype) )
                    Number += 1
                    Count += 1
                except Exception as e:
                    print(e)
                    
            except FileExistsError:
                search.pop(search.index(img))
                search.append(img)
                Count -= 1
        else:
            print(img,"was blacklisted")
    else:
        print(img,"was blacklisted")
if Count <= 0:
    print("Nothing has been renamed")
elif crtdate_rename == True:
    print('Renamed {} files as CreationDate_x'.format(Count))
else:
    print('Renamed {} files as {}_x'.format(Count, RenameName))
finished = time.perf_counter()
print(f"Finished in {round(finished - start, 4)} seconds")
input('Press exit or enter to close')