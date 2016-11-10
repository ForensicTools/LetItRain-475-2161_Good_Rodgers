# The main wrapper for the tool

import argparse
import os
import sys
import gdrive
import hashChecker
#import dbox
import report

parser = argparse.ArgumentParser()
parser.add_argument('-md5file', default="None", help='The user-given txt file of md5 hashes')
parser.add_argument('-sha256file', default="None", help='The user-given txt file of sha256 hashes')
parser.add_argument('-sha1file', default="None", help='The user-given txt file of sha1 hashes')
parser.add_argument('--positive', action="store_true", dest="positive", help='Enable positive hashing')
parser.add_argument('--negative', action="store_true", dest="negative", help='Enable negative hashing')
parser.add_argument('--gdrive', action="store_true", dest="drive", help='Analyzing Google Drive')
parser.add_argument('--dropbox', action="store_true", dest="dropbox", help='Analyzing Dropbox')
args = parser.parse_args()

# Checks to make sure options are parsed correctly
# If there are errors, returns 0 which should exit program when returned to main
def error_check(args):
    if args.positive and args.negative:
        sys.exit("ERROR: Choose positive or negative, cannot do both.")
    if not args.positive and not args.negative:
        sys.exit("ERROR: Please indicate whether positive or negative")
    if not args.drive and not args.dropbox:
        sys.exit("ERROR: Please indicate Google Drive or Dropbox")
    if args.drive and args.dropbox:
        sys.exit("ERROR: Cannot perform Google Drive and Dropbox analysis. Pick one.")

def main():
    input_parameter_test = error_check(args)
    if args.dropbox:
        folder_name = dbox.dropbox()
    else:
        folder_name = gdrive.google_drive()
    results = hashChecker.hash_checker(folder_name, args)
    report.generate_report(results, folder_name)

if __name__ == '__main__':
    main()
