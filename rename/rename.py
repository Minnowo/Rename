import os
import random 
from re import compile, match
from datetime import datetime

def natural_sort_key(s, _nsre=compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(s)]

def get_sep(string, *, throw_error = False, error = ""):
    """Get the separator character from a string -> sep=|"""
    _ = string.find("=")
    
    if _ == -1:
        if throw_error: raise Exception(error)
        return "|"

    _ = string[_ + 1:] # take everything after the =
    _ = _[:-1]         # remove the last character of the string (assumes \n)
    return _

def handle_undo(file : list):
    """Reads a list of [.rn] files and renames all existing files back to before being renamed for each file"""
    cwd = os.getcwd()

    for f in file:

        if os.path.exists(f):

            if os.path.isdir(f):
                cwd = os.getcwd()

                try:
                    dir  = os.path.abspath(f) 
                    os.chdir(dir)
                    paths = filter(lambda x : x.endswith(".rn"), os.listdir()) # grab any .rn files 

                finally:
                    os.chdir(cwd)

            if os.path.isfile(f):
                dir  = os.path.dirname(f) 
                paths = [os.path.basename(f)]

            for rn in paths:

                full_path = os.path.join(dir, rn)
                print(full_path)

                try:
                    with open(full_path, "rb") as rn_file:
                        _ = rn_file.readline().decode()
                        sep = get_sep(_, throw_error=True, error="Invalid rn file cannot get separator")
                        
                        for line in rn_file:

                            lined = line.decode()

                            if lined.startswith("ERROR" + sep):
                                if lined.count(sep) != 2: # if there is an error there will be 3 occurance of sep
                                    continue
                            
                            old_n, _, new_n = lined.partition(sep)

                            old_path = os.path.join(dir, old_n)
                            new_path = os.path.join(dir, new_n[:-1])

                            if os.path.exists(new_path):
                                os.rename(new_path, old_path)
                                print(f"   {new_n.rstrip()} {sep} {old_n.rstrip()}")

                except Exception as e:
                    print(e) 
                    continue
                
    
    os.chdir(cwd)

def get_parser():
    import argparse

    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]... URL...",
        add_help=False,
    )

    general = parser.add_argument_group("General Options")
    general.add_argument(
        "-h", "--help",
        action="help",
        help="Print this help message and exit",
    )

    rename = parser.add_argument_group("Rename Options")
    rename.add_argument(
        "-i", "--input",
        dest="inputs", metavar="FOLDER", action="append",
        help="Specify input directories"
    )
    rename.add_argument(
        "-f", "--format",
        dest="format", metavar="FORMAT",
        help="Specify the format to rename"
    )
    rename.add_argument(
        "-r", "--replace",
        dest="replace", metavar="REPLACE:WITH", action="append",
        help="Replace any occurance of anything before the last : with anything after the last :"
    )
    rename.add_argument(
        "-u", "--undo",
        dest="undo_file", metavar="FILE", action="append",
        help="Undo any renaming done using the provided .rn file"
    )
    rename.add_argument(
        "-sw", "--start-with",
        dest="start_with", metavar="STR", action="append",
        help="Only rename files that start with the given string (multiple --start-with can be specified)"
    )
    rename.add_argument(
        "-ew", "--ends-with",
        dest="ends_with", metavar="STR", action="append",
        help="Only rename files that end with the given string (multiple --ends-with can be specified)"
    )
    rename.add_argument(
        "-m", "--match",
        dest="matches", metavar="REGEX", action="append",
        help="Only rename if the filename matches any of the given regex"
    )
    

    after_rename = parser.add_argument_group("Other Options")
    after_rename.add_argument(
        "--no-file",
        dest="no_rn_file", action="store_true",
        help="Do not create .rn file"
    )
    after_rename.add_argument(
        "-a", "--append-rn",
        dest="append_rn_data", action="store_true",
        help="Should .rn file data be written to any existing rn files"
    )
    
    parser.add_argument(
        "--date-formats",
        dest="custom_date_formats", action="store_true",
        help="Show all custom date formats"
    )
    parser.add_argument(
        "--format-help",
        dest="display_formats", action="store_true",
        help="List renaming formats and exit"
    )
    parser.add_argument(
        "-s", "--sep",
        dest="sep", metavar="SEP", 
        help=".rn file sep char"
    )

    return parser


class Renamer:
    """
    A simple wrapper around os.rename that handles printing to the console and logging into a file
    
        __init__(directory, log_file, overwrite_existing, no_log)

            - directory : the directory where files are going to be renamed
            - log_file  : the name of the log file
            - overwrite_existing : overwrite existing logfile, otherwise appends
            - no_log : doesn't write anything to the log file

        
        rename(file_name, new_name) : renames the given file

            - file_name : the name of the file relative to the given directory from __init__
            - new_name  : the new name of the file relative to the given directory from __init__


        log(text) : write the given text to the log file

            - text : bytes / encoded text NOT string -> use string.encode()


        close() : closes the log file

    """
    def __init__(self, directory, log_file, *, sep = "|", overwrite_existing = True, no_log = False) -> None:
        
        self.directory = directory
        self.log_file_name = log_file

        self.logger = None
        self.sep = sep

        if no_log:
            return

        # get the path to the rn file
        _ = os.path.join(directory, log_file)

        # if file exists, and the user wants to append logs to existing .rn file, 
        # read the file and get the separator character,
        if os.path.exists(_) and not overwrite_existing:
            with open(_, "r") as fff:
                self.sep = get_sep(fff.readline())

            self.logger = open(_, "ab")  

        # else just override the old file
        else:
            # reading / writing as bytes because of foreign characters
            self.logger = open(_, "wb")    
            self.logger.write(f"sep={self.sep}\n".encode())

    def close(self):
        if self.logger:
            self.logger.close()

    def log(self, text):
        if not self.logger:
            return 

        self.logger.write(text)

    def rename(self, file_name, new_name):

        try:
            os.rename(os.path.join(self.directory, file_name), os.path.join(self.directory, new_name))
            print(f"   {file_name} {self.sep} {new_name}")
            self.log(f"{file_name}{self.sep}{new_name}\n".encode())
        except:
            print(f"ERROR   {file_name} {self.sep} {new_name}") 
            self.log(f"ERROR|{file_name}{self.sep}{new_name}\n".encode())
            

class DigitTemplateGenerator:
    """A class that returns a template string formatted with digits
    
    formats strings containing any 2 templates:
       $[n:z]   where n is the starting number and z is the ending number (increment is 1 by default)
       $[n:i:z] where n is the starting number, i is the increment and z is the ending number

    example usage:
        
        template = "sample_$[1:100]"

        d_format = DigitFormatter(template)
        d_format.get_formatted_text() # -> sample_1
        d_format.get_formatted_text() # -> sample_2
        d_format.get_formatted_text() # -> sample_3
         
    """
    # split function for the digit formats $[1:1] or $[1:1:1]
    DIGIT_SPLIT  = compile(r"\$\[-?\d+(?:\:-?\d+)?:-?\d+\]").split

    # matches $[1:9] or $[1:1:9]
    DIGIT_MATCH  = compile(r"\$\[(-?\d+)(?:\:(-?\d+))?\:(-?\d+)\]")

    def __init__(self, template : str) -> None:
        
        self.split = [i for i in self.DIGIT_SPLIT(template)]
        self.digits = []
        self.digit_counter = []
        self.end = len(self.split)

        for i in self.DIGIT_MATCH.findall(template):
            increment = 1 

            if i[1]:
                increment = int(i[1])

            # format the digits as ints (start, increment, max)
            self.digits.append((int(i[0]), increment, int(i[2])))  

        self.reset()
            
    def get_next_string(self):
        """Gets the name formatted with the current digits and increments all the digits"""
        # begin building the name
        name = ""
        count = 0                                # loop count 
        index = 0                                # index of the current digit position
        for i in self.split:

            # make sure its not the first or last loop
            if count > 0 and count < self.end:
                
                # tuple (start, zfill) -> the starting digit, and the zfill 
                d = self.digit_counter[index]         

                # append the current digit to the string and apply zfill
                name += f"{d[0]}".zfill(d[1])         

                # (start, zfill)[0] < (start, increment, max)[2] 
                # if less than max increase by the increment amount
                if d[0] < self.digits[index][2]:

                    self.digit_counter[index][0] += self.digits[index][1]

                # move to next index 
                index += 1 
            
            # append the string
            name += i 
            count += 1

        return name 

    def reset(self):
        """Resets all the counters for each digit"""
        # reset / init the digit counter array 
        self.digit_counter = []
        for dig in self.digits: 
            # dig[0] = start number
            # dig[2] = end number
            start = dig[0] 
            pad_zeros = len(str(dig[2]))

            self.digit_counter.append([start, pad_zeros])


class TextFormatter:

    def __init__(self, template) -> None:
        self.template = template

    def add_context(self, context):
        pass 

    def format_text(self, text):
        pass 


class DateFormatter(TextFormatter):

    SUB_MAP = {
        "FDM" : compile(r"\$\[FDM\]").sub,
        "FDC" : compile(r"\$\[FDC\]").sub,
        "CD"  : compile(r"\$\[CD\]").sub
    }

    # matches $[FDM]  or $[FDC] pr $[CD]
    MATCH_SIMPLE_DATE = compile(r"\$\[(FDM|FDC|CD)\]")
    
    # matches $[FDM: 'anything that is not [ or ]' ]
    # matches $[FDC: 'anything that is not [ or ]' ]
    MATCH_CUSTOM_DATE = compile(r"\$\[(FDM|FDC|CD):([^\]]+)\]")      

    def __init__(self, template, *, default_date_format = "%Y-%m-%d", require_file_exist = True) -> None:
        
        TextFormatter.__init__(self, template)

        # simple date sub will just sub everything and there is only 2 options so just remove duplicates
        self.simple_date_format = set(self.MATCH_SIMPLE_DATE.findall(template))

        # list of tuple -> (DM / DC, custom date format)
        self.custom_date_format = self.MATCH_CUSTOM_DATE.findall(template)

        self.file_name = ""

        self.date_format = default_date_format
        self.require_file_exist = require_file_exist
        
    def add_context(self, context):
        """Set the filename for formatting file date created / modified"""
        
        self.file_name = context

    def format_text(self, templage):

        name = templage
        file_date_created = 0
        file_date_modified = 0

        if os.path.isfile(self.file_name):
            file_date_created = os.stat(self.file_name).st_ctime
            file_date_modified = os.stat(self.file_name).st_mtime

        elif self.require_file_exist:
            raise Exception("DateFormatter.get_formatted_text -> given file does not exist, requires the file exists")
            
        for i in self.simple_date_format:

            if i == "FDM":
                name = self.SUB_MAP[i](datetime.fromtimestamp(file_date_modified).strftime(self.date_format), name)
            
            elif i == "FDC":
                name = self.SUB_MAP[i](datetime.fromtimestamp(file_date_created).strftime(self.date_format), name)

            elif i == "CD":
                name = self.SUB_MAP[i](datetime.fromtimestamp(datetime.now().timestamp()).strftime(self.date_format), name)


        for i in self.custom_date_format:

            if i[0] == "FDM":
                name = self.MATCH_CUSTOM_DATE.sub(datetime.fromtimestamp(file_date_modified).strftime(i[1]), name, 1)

            elif i[0] == "FDC":
                name = self.MATCH_CUSTOM_DATE.sub(datetime.fromtimestamp(file_date_created).strftime(i[1]), name, 1)
                
            elif i[0] == "CD":
                name = self.MATCH_CUSTOM_DATE.sub(datetime.fromtimestamp(datetime.now().timestamp()).strftime(i[1]), name, 1)
        
        return name

def main():

    parser = get_parser()
    args = parser.parse_args()

    if args.display_formats:
        print("-- Formats --")
        print("$[EXT]          : the files extension") 
        print("$[0:10]         : a digit that starts at 0 and increments by 1 until 10")
        print("$[0:2:10]       : a digit that starts at 0 and increments by 2 until 10")
        print("$[RND:0:999]    : a random number anywhere from 0-999")
        print("$[FDM]          : the date modified")   
        print("$[FDC]          : the date created")   
        print(r"$[CD:%Y-%m-%d] : specify a custom date format -> run --date-formats to see all of them")
        return

    if args.custom_date_formats:
        print("""
Code  Example     Description
%a    Sun         Weekday as locale's abbreviated name.
%A    Sunday      Weekday as locale's full name.
%w    0           Weekday as a decimal number, where 0 is Sunday and 6 is Saturday.
%d    08          Day of the month as a zero-padded decimal number.
%-d   8           Day of the month as a decimal number. (Platform specific)
%b    Sep         Month as locale's abbreviated name.
%B    September   Month as locale's full name.
%m    09          Month as a zero-padded decimal number.
%-m   9           Month as a decimal number. (Platform specific)
%y    13          Year without century as a zero-padded decimal number.
%Y    2013        Year with century as a decimal number.
%H    07          Hour (24-hour clock) as a zero-padded decimal number.
%-H   7           Hour (24-hour clock) as a decimal number. (Platform specific)
%I    07          Hour (12-hour clock) as a zero-padded decimal number.
%-I   7           Hour (12-hour clock) as a decimal number. (Platform specific)
%p    AM          Locale's equivalent of either AM or PM.
%M    06          Minute as a zero-padded decimal number.
%-M   6           Minute as a decimal number. (Platform specific)
%S    05          Second as a zero-padded decimal number.
%-S   5           Second as a decimal number. (Platform specific)
%f    000000      Microsecond as a decimal number, zero-padded on the left.
%z    +0000       UTC offset in the form ±HHMM[SS[.ffffff]] (empty string if the object is naive).
%Z    UTC         Time zone name (empty string if the object is naive).
%j    251         Day of the year as a zero-padded decimal number.
%-j   251         Day of the year as a decimal number. (Platform specific)
%x    09/08/13    Locale's appropriate date representation.
%X    07:06:05    Locale's appropriate time representation.
%%    %           A literal '%' character.

%U    36          Week number of the year (Sunday as the first day of the week) as a zero padded decimal number.
                  All days in a new year preceding the first Sunday are considered to be in week 0.

%W    35          Week number of the year (Monday as the first day of the week) as a decimal number.
                  All days in a new year preceding the first Monday are considered to be in week 0.

%c    Sun Sep 8 07:06:05 2013       Locale's appropriate date and time representation.""")
        return 

    if args.undo_file:
        handle_undo(args.undo_file)
        return

    if not args.inputs:
        parser.error("No inputs specified")
        return 

    if not args.format and not args.replace:
        print("No output format or replace specified use -f \"FORMAT\" to specify a format --format-help for more info\nor -r 'word:replacement' to replace words")
        return

    # sub functions
    RE_SUB_EXT    = compile(r"\$\[EXT\]").sub  # repalce file extension
    MATCH_RAND    = compile(r"\$\[RND\:(\d+)\:(\d+)\]")

    _replace = {} 
    if args.replace:                  # replace specified

        for i in args.replace:        # go through all given strings
            
            _ = i.rsplit(":", 1)      # split at last occurance of :
            
            if len(_) == 2:           # if there is not 2 items skip
                _replace[_[0]] = _[1] # set dict 

    if not args.start_with:
        args.start_with = []

    if not args.ends_with:
        args.ends_with = []

    if args.format:
        
        digit_formatter = DigitTemplateGenerator(args.format)
        date_formatter  = DateFormatter(args.format)
        
        def format_func(text : str):
             # get the file extension
            ext = text.rsplit(".", 1)
            ext = ext[-1] if len(ext) > 1 else ""

            name = digit_formatter.get_next_string()
            date_formatter.add_context(text)
            name = date_formatter.format_text(name)

            for i in MATCH_RAND.findall(name):
                name = MATCH_RAND.sub(str(random.randint(int(i[0]), int(i[1]))), name, 1)
            # name = RE_SUB_RAND(random.ra)
            # replace the $[EXT] with the file extension 
            name = RE_SUB_EXT(ext, name) 
            return name

    else:
        
        def format_func(text : str):
            for key, value in _replace.items():
                text = text.replace(key, value)

            return text 
    

    items  = {"directories" : set(), "files" : set()}

    for i in args.inputs:

        if os.path.exists(i):
            if os.path.isdir(i):
                items["directories"].add(os.path.abspath(i))

            elif os.path.isfile(i):
                items["files"].add(os.path.abspath(i))

    for dir in items["directories"]:

        renamer = Renamer(dir, ".rn", 
            sep = args.sep or "|",
            overwrite_existing = not args.append_rn_data, 
            no_log = args.no_rn_file)

        # remember the starting directory
        cwd = os.getcwd()
        try:

            os.chdir(dir)              # change into the target directory

            for root, dirs, files in os.walk(dir):                  # get directories
                for file in sorted(files, key=natural_sort_key): # get all files naturally sorted
                    
                    if file == ".rn" :
                        continue
                    
                    # if the filename does not match any of the regex skip
                    if args.matches:
                        if not any(match(regex, file) for regex in args.matches):
                            continue
                    
                    # if the filename does not startwith any of the given strings skip
                    if any([not file.startswith(i) for i in args.start_with]):
                        continue

                    # if the filename does not endwith and of the given strings skip
                    if any([not file.endswith(i) for i in args.ends_with]):
                        continue

                    name = format_func(file)

                    renamer.rename(file, name)

                break # only want the top level directories files

        finally:
            os.chdir(cwd)

        # close our log file
        renamer.close()

if __name__ == "__main__":
    main()