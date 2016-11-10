# This file will grab the hashes from the file generation and compare them to
# hashes gotten from user-given files. Can return positive (files that do match)
# or negative (files that don't match) hash results

import argparse
import os
from FileObject import FileObject

parser = argparse.ArgumentParser()
parser.add_argument('-md5file', default="None", help='The user-given txt file of md5 hashes')
parser.add_argument('-sha256file', default="None", help='The user-given txt file of sha256 hashes')
parser.add_argument('-sha1file', default="None", help='The user-given txt file of sha1 hashes')
parser.add_argument('--positive', action="store_true", dest="positive", help='Enable positive hashing')
parser.add_argument('--negative', action="store_true", dest="negative", help='Enable negative hashing')
args = parser.parse_args()

# Checks to make sure options are parsed correctly
# If there are errors, returns 0 which should exit program when returned to main
def error_check(args):
    if args.positive and args.negative:
        print("ERROR: Choose positive or negative, cannot do both.")
        return 0
    if not args.positive and not args.negative:
        print("ERROR: Please indicate whether positive or negative")
        return 0

# Creates a 2D list of the user-submitted hashes. Will return a list of lists.
# If one of the files for hashes wasn't included, that spot will be an empty list
def create_hash_lists(args):
    master_hash_list = list()
    if args.md5file != "None":
        md5_hashes = return_list_from_file(args.md5file)
        master_hash_list.append(md5_hashes)
    else:
        md5_hashes = ["None"]
        master_hash_list.append(md5_hashes)
    if args.sha256file != 'None':
        sha256_hashes = return_list_from_file(args.sha256file)
        master_hash_list.append(sha256_hashes)
    else:
        sha256_hashes = ["None"]
        master_hash_list.append(sha256_hashes)
    if args.sha1file != 'None':
        sha1_hashes = return_list_from_file(args.sha1file)
        master_hash_list.append(sha1_hashes)
    else:
        sha1_hashes = ["None"]
        master_hash_list.append(sha1_hashes)
    return master_hash_list

# TODO: Create list of objects of file names and hashes gathered from gdrive and dropbox
def get_hashes_from_download(folder_name):
    if os.path.exists(folder_name):
        master_hash_list = list()
        # parse deleted
        if os.path.exists(folder_name + "/deleted"):
            # parse deleted Google docs
            if os.path.exists(folder_name + "/deleted/_google"):
                hash_list = collect_hashes(folder_name + "/deleted/_google")
                master_hash_list = add_hashes_to_master_list(master_hash_list, hash_list)
            # call non-Google doc deleted items hash collector
            hash_list = collect_hashes(folder_name + "/deleted")
            master_hash_list = add_hashes_to_master_list(master_hash_list, hash_list)
        # parse regular files
        if os.path.exists(folder_name + "/regular"):
            # parse deleted Google docs
            if os.path.exists(folder_name + "/regular/_google"):
                hash_list = collect_hashes(folder_name + "/regular/_google")
                master_hash_list = add_hashes_to_master_list(master_hash_list, hash_list)
            # call non-Google doc items hash collector
            hash_list = collect_hashes(folder_name + "/regular")
            master_hash_list = add_hashes_to_master_list(master_hash_list, hash_list)
        return master_hash_list
    else:
        print{"ERROR: Folder does not exist. Exitting..."}
        return 0

# Concatenates the master_list and the new hash_list
def add_hashes_to_master_list(master_list, hashes_to_add):
    if not hashes_to_add:
        return master_list
    for obj in hashes_to_add:
        if isinstance(obj, FileObject):
            master_list.append(obj)
    return master_list

# takes in current hash lists and appends newly found hash values to them
def collect_hashes(path):
    if os.path.exists(path + "/_hashes.txt"):
        hash_file = open(path + "/_hashes.txt", 'rb')
        hash_list = list()
        count = 0
        for line in hash_file:
            if count % 4 == 0:
                hash_obj = FileObject()
                hash_obj.set_name(line)
            if count % 4 == 1:
                line_split = line.split(' ')
                hash_obj.set_md5(line_split[1])
            if count % 4 == 2:
                line_split = line.split(' ')
                hash_obj.set_sha1(line_split[1])
            if count % 4 == 3:
                line_split = line.split(' ')
                hash_obj.set_sha256(line_split[1])
                hash_list.append(hash_obj)
            count = count + 1
        return hash_list
    else:
        print("Hash file does not exist for " + path)

# Performs hash matching, alters the match status in the objects accordingly
# then returns the objects list
def hash_matching(list_of_downloaded_objects, read_in_hashes):
    md5 = read_in_hashes[0]
    sha256 = read_in_hashes[1]
    sha1 = read_in_hashes[2]

    if md5:
        for hash in md5:
            for obj in list_of_downloaded_objects:
                if obj.get_md5().strip() == hash.strip():
                    obj.set_md5_hash_match(True)
    if sha256:
        for hash in sha256:
            for obj in list_of_downloaded_objects:
                if obj.get_sha256().strip() == hash.strip():
                    obj.set_sha256_hash_match(True)
    if sha1:
        for hash in sha1:
            for obj in list_of_downloaded_objects:
                if obj.get_sha1().strip() == hash.strip():
                    obj.set_sha1_hash_match(True)
    return list_of_downloaded_objects

# Performs positive hashing. Returns objects that match given hashes.
def positive_hashing(list_of_downloaded_objects):
    positive_md5 = list()
    positive_sha256 = list()
    positive_sha1 = list()
    for obj in list_of_downloaded_objects:
        if obj.get_md5_match() == True:
            positive_md5.append(obj)
        if obj.get_sha256_match() == True:
            positive_sha256.append(obj)
        if obj.get_sha1_match() == True:
            positive_sha1.append(obj)
    results = [positive_md5, positive_sha1, positive_sha256]
    return results

# Performs negative hashing. Returns object that don't match given hashes
def negative_hashing(list_of_downloaded_objects):
    negative_md5 = list()
    negative_sha256 = list()
    negative_sha1 = list()
    for obj in list_of_downloaded_objects:
        if obj.get_md5_match() == False:
            negative_md5.append(obj)
        if obj.get_sha256_match() == False:
            negative_sha256.append(obj)
        if obj.get_sha1_match() == False:
            negative_sha1.append(obj)
    results = [negative_md5, negative_sha1, negative_sha256]
    return results

# Reads in a specified file full of hashes (one hash per line) and returns a list
# of the hashes
def return_list_from_file(read_file):
    hash_list = list()
    file1 = open(read_file, 'rb')
    for line in file1:
        hash_list.append(line)
    return hash_list

def main():
    res = error_check(args)
    if res == 0:
        return 0
    master_list = create_hash_lists(args)
    folderName = "gdrive_dump_2016-10-28--17-43-54"
    downloaded_files_objects = get_hashes_from_download(folderName)
    if downloaded_files_objects == 0:
        return 0
    hash_matches = hash_matching(downloaded_files_objects, master_list)
    if args.positive == True:
        positive_matches = positive_hashing(hash_matches)
    else:
        negative_matches = negative_hashing(hash_matches)

main()
