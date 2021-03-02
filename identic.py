import hashlib
import os
from collections import deque
import argparse

hashes = {} #stores hashes as keys and list of duplicate files/directories as values
sizes = {}  #stores hashes as keys and size of duplicate files/directories as values

def duplicate():    #according to hashes of files/directories, this function creates a list of duplicate files/directories
    duplicates = []
    def myFunc(tuple):  #in order to sort alphabetically
        return tuple[1]
    def myFunc2(tuple): #in order to sort in descending order
        return tuple[0]
    if args.s and (args.c or not(args.n)):  #if -s option is valid, creates a list of tuples which consist of size and list of duplicate files/directories
        for hash in hashes:
            if not(len(hashes[hash]) == 1):
                hashes[hash].sort()
                duplicates.append((sizes[hash],hashes[hash]))
        duplicates.sort(key = myFunc)   #if size of some duplicate sets are equal, sorts them alphabetically
        duplicates.sort(key = myFunc2, reverse = True) #sorts duplicate sets according to their size in descending order 
    else:   #if -s option is not valid, creates a list of lists which consist of duplicate files/directories
        for hash in hashes:
            if not(len(hashes[hash]) == 1):
                hashes[hash].sort()
                duplicates.append(hashes[hash])
        duplicates.sort()   #sorts duplicate sets alphabetically
    return duplicates

def traverseFile(directory):    #traverses the tree of directories and calculates the hash values of files in it
    q = deque([directory])
    while q:
        currentDir = q.popleft()
        dirElements = os.listdir(currentDir)
        for element in dirElements:
            currentItem = currentDir + "/" + element
            if os.path.isfile(currentItem):
                if not(args.n): #if -c option is valid
                    with open(currentItem, "rb") as f:
                        content = f.read()
                    hash = hashlib.sha256(content).hexdigest()
                elif (not(args.c)) and args.n:  #if -n option is valid
                    hash = hashlib.sha256(element.encode()).hexdigest()
                else:   #if -cn option is valid
                    with open(currentItem, "rb") as f:
                        content = f.read()
                    hash = (hashlib.sha256(content).hexdigest(), hashlib.sha256(element.encode()).hexdigest())
                size = os.path.getsize(currentItem)
                if hash in hashes:
                    if not(currentItem in hashes[hash]):
                        hashes[hash].append(currentItem)
                else:
                    hashes[hash] = [currentItem]
                    sizes[hash] = size
            elif os.path.isdir(currentItem):
                q.append(currentItem)

def traverseDirectory(directory):   #traverses the tree of directories and calculates the hash values of directories in it
    children1 = []  #stores the hashes of children of current directory, according to -c (when -c or -cn option is valid) or -n option
    children2 = []  #stores the hashes of children of current directory, according to -n option when -cn option is valid
    size = 0    #stores the sizes children of current directory
    dirElements = os.listdir(directory)
    for element in dirElements:
        currentItem = directory + "/" + element
        if os.path.isfile(currentItem):
            if not(args.n): #if -c option is valid
                with open(currentItem, "rb") as f:
                    content = f.read()
                hash = hashlib.sha256(content).hexdigest()
                children1 = children1 + [hash]
            elif (not(args.c)) and args.n:  #if -n option is valid
                hash = hashlib.sha256(element.encode()).hexdigest()
                children1 = children1 + [hash]
            else:   #if -cn option is valid
                with open(currentItem, "rb") as f:
                        content = f.read()
                hash1 = hashlib.sha256(content).hexdigest()
                hash2 = hashlib.sha256(element.encode()).hexdigest()
                children1 = children1 + [hash1]
                children2 = children2 + [hash2]
            size = size + os.path.getsize(currentItem)
        elif os.path.isdir(currentItem):
            hash = traverseDirectory(currentItem)
            if args.c and args.n:   #if -cn option is valid
                children1 = children1 + [hash[0]]
                children2 = children2 + [hash[1]]
            else:   #if -c or -n option is valid
                children1 = children1 + [hash]
            size = size + sizes[hash]
    h = hashDirectory(directory, children1, children2)  #calculates the hash of current directory according to hashes of its children
    if h in hashes:
        if not(directory in hashes[h]):
            hashes[h].append(directory)
    else:
        hashes[h] = [directory]
        sizes[h] = size
    return h

def hashDirectory(directory, children1, children2): #calculates the hash of a directory according to hashes of its children
    name = os.path.basename(directory) 

    children1.sort()
    children2.sort()

    if (not(args.c)) and args.n:    #if -n option is valid, concatenates the hash of the name of the directory at the beginning
        hashName = hashlib.sha256(name.encode()).hexdigest()
        children1.insert(0, hashName)
    elif args.c and args.n: #if -cn option is valid, concatenates the hash of the name of the directory at the beginning
        hashName = hashlib.sha256(name.encode()).hexdigest()
        children2.insert(0, hashName)

    dirEntries1 = ""    #concatenates all of the elements
    for i in children1:
        dirEntries1 = dirEntries1 + i
    dirEntries2 = ""    #concatenates all of the elements
    for j in children2:
        dirEntries2 = dirEntries2 + j

    if args.c and args.n:   #if -cn option is valid, returns a tuple of -c hash and -n hash of the directory
        return (hashlib.sha256(dirEntries1.encode()).hexdigest(), hashlib.sha256(dirEntries2.encode()).hexdigest())
    else:   #if -c or -n option is valid, returns the hash of the directory
        return hashlib.sha256(dirEntries1.encode()).hexdigest()

def parse():    #parses the command line arguments
    parser = argparse.ArgumentParser()
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("-f", help = "File flag", action = "store_true", default = False)
    group1.add_argument("-d", help = "Directory flag", action = "store_true", default = False)
    parser.add_argument("-c", help = "Content flag", action = "store_true", default = False)
    parser.add_argument("-n", help = "Name flag", action = "store_true", default = False)
    parser.add_argument("-s", help = "Size flag", action = "store_true", default = False)
    parser.add_argument("dirs", help = "Directories will be checked", type = str, nargs = "*")
    return parser.parse_args()

args = parse()  #stores the values of the flags and directories if it is given

if not(args.d): #if -f option is valid calls traverseFile(directory) function
    if args.dirs == []: #if there is no given directory, traverses the current directory
        traverseFile(os.getcwd())
    else:   #if there are given directories, traverses all of the directories one by one
        for dir in args.dirs:
            traverseFile(os.path.abspath(dir))

elif (not(args.f)) and args.d: #if -d option is valid calls traverseDirectory(directory) function
    if args.dirs == []: #if there is no given directory, traverses the current directory
        traverseDirectory(os.getcwd())
    else:   #if there are given directories, traverses all of the directories one by one
        for dir in args.dirs:
            traverseDirectory(os.path.abspath(dir))

duplicates = duplicate()    #stores the duplicate files/directories with/without their sizes

if args.s and (args.c or not(args.n)):  #if -s option is valid, prints the duplicate files/directories with their sizes
    for size,paths in duplicates:
        for path in paths:
            print(path + "\t" + str(size))
        print()
else:   #if -s option is not valid, prints the duplicate files/directories
    for paths in duplicates:
        for path in paths:
            print(path)
        print()