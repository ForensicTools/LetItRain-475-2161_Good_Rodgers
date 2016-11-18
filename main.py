# The main wrapper for the tool

import argparse
import os
import sys
import gdrive
import hash_checker
import dbox
import report
import time
from datetime import datetime

# Checks to make sure options are parsed correctly
# If there are errors, returns 0 which should exit program when returned to main
def error_check(args):
    if args.positive and args.negative:
        sys.exit("ERROR: Choose positive or negative, cannot do both.")
    if not args.drive and not args.dropbox:
        sys.exit("ERROR: Please indicate Google Drive or Dropbox")
    if args.drive and args.dropbox:
        sys.exit("ERROR: Cannot perform Google Drive and Dropbox analysis. Pick one.")

def create_log_file(timestamp):
    log_file = open("let_it_rain_" + timestamp + ".log", "w")
    return log_file

def log_and_print(log_file, log_entry, newline=True):
    if newline:
        log_file.write(log_entry + "\n")
        print(log_entry)
    else:
        log_file.write(log_entry)
        print(log_entry, end="", flush=True)

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
    start_time = datetime.now()
    # Input argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--gdrive', action="store_true", dest="drive", help='Analyzing Google Drive')
    parser.add_argument('--dropbox', action="store_true", dest="dropbox", help='Analyzing Dropbox')
    parser.add_argument('--positive', action="store_true", dest="positive", help='Enable positive hashing')
    parser.add_argument('--negative', action="store_true", dest="negative", help='Enable negative hashing')
    parser.add_argument('--md5file', default="None", help='The user-given txt file of md5 hashes')
    parser.add_argument('--sha256file', default="None", help='The user-given txt file of sha256 hashes')
    parser.add_argument('--sha1file', default="None", help='The user-given txt file of sha1 hashes')
    args = parser.parse_args()
    input_parameter_test = error_check(args)
    log_file = create_log_file(timestamp)
    log_and_print(log_file, "\n#######################################")
    log_and_print(log_file, "############## LetItRain ##############")
    log_and_print(log_file, "#######################################\n")
    log_and_print(log_file, "Time started: " + timestamp + "\n")
    if args.dropbox:
        log_and_print(log_file, "Running Dropbox tool...\n")
        folder_name, file_list, deleted_file_list = dbox.dbox(timestamp, log_file)
    else:
        log_and_print(log_file, "Running Google Drive tool...\n")
        folder_name, file_list, deleted_file_list = gdrive.google_drive(timestamp, log_file)
    if args.positive:
        log_and_print(log_file, "Performing positive hashing...")
        results = hashChecker.hash_checker(folder_name, args)
        log_and_print(log_file, "Done!")
    elif args.negative:
        log_and_print(log_file, "Performing negative hashing...")
        results = hashChecker.hash_checker(folder_name, args)
    else:
        results = []
    end_time = datetime.now()
    run_time = str(end_time - start_time)
    log_and_print(log_file, "Total run time: " + run_time)
    log_and_print(log_file, "Generating report... ", False)
    report.generate_report(results, folder_name, args, timestamp, run_time, file_list, deleted_file_list)
    log_and_print(log_file, "Done!")
    log_and_print(log_file, "Exiting...")
    log_file.close()

if __name__ == '__main__':
    main()
