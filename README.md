# CmpE230-DuplicateFinder

This project searches for identical contents and/or names of files/directories.

It can take flags as command line arguments in order to specify the wanted search. Flags may be -f/-d, -c/-n, -s. -f and -d means search for identical files and directories, respectively. They cannot be used at the same time. By default, program is executed with -f option. -c and -n means search for identical files/directories according to contents and names, respectively. They can be used at the same time, -cn, which means search for identical files/directories according to both contents and names. By default, program is executed with -c option. -s means sort according to size of duplicates and write their sizes at the end of searching. While using the option -n, -s option is not available due to different size of duplicates.

Also, program can take a list of directories as command line arguments in order to search in these directories. If there is no specified directory, current directory is searched. Otherwise, each given directory is searched one by one.
