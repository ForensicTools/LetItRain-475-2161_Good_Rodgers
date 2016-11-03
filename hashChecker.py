# This file will grab the hashes from the file generation and compare them to
# hashes gotten from user-given files. Can return positive (files that do match)
# or negative (files that don't match) hash results

import argparse

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
# TODO: Create positive hashing method
# TODO: Create negative hashing method

# Reads in a specified file full of hashes (one hash per line) and returns a list
# of the hashes
def return_list_from_file(read_file):
    hash_list = list()
    file1 = open(read_file, 'r')
    for line in file1:
        hash_list.append(line)
    return hash_list

def main():
    res = error_check(args)
    if res == 0:
        return 0
    master_list = create_hash_lists(args)

main()
