# Contains report generation code

import os
import platform
from file_object import FileObject

# Write to the txt file the hashing results
def write_to_report_file(results, folder_name, args, timestamp, run_time, file_list, deleted_file_list):
    report_file = open("{}/report.txt".format(folder_name), 'w')
    report_file.write("#######################################\n")
    report_file.write("############## LetItRain ##############\n")
    report_file.write("#######################################\n\n")
    report_file.write("###############\n")
    report_file.write("RUN INFORMATION\n")
    report_file.write("###############\n")
    # Write OS info to report
    report_file.write("OS: {}\n".format(str(platform.platform())))
    report_file.write("Folder name: {}\n".format(folder_name))
    report_file.write("Time started: {}\n".format(timestamp))
    report_file.write("Total run time: {}\n".format(run_time))
    if args.positive or args.negative:
        if args.md5file != "None":
            report_file.write("MD5 hashing file: {}\n".format(args.md5file))
        if args.sha1file != "None":
            report_file.write("SHA1 hashing file: {}\n".format(args.sha1file))
        if args.sha256file != "None":
            report_file.write("SHA256 hashing file: {}\n".format(args.sha256file))
    report_file.write("\n###################\n")
    report_file.write("HASHING INFORMATION\n")
    report_file.write("###################\n")
    if args.positive:
        report_file.write("Positive Hashing Performed\n")
        hash_matching_performed = True
    elif args.negative:
        report_file.write("Negative Hashing Performed\n")
        hash_matching_performed = True
    else:
        report_file.write("No hash matching requested.\n")
        hash_matching_performed = False
    if hash_matching_performed:
        if not results[0] == [] and not args.md5file == "None":
            report_file.write("MD5:\n")
            for res in results[0]:
                report_file.write("{} - {}\n".format(res.get_name().strip(), res.get_md5()))
        if not results[1] == [] and not args.sha1file == "None":
            report_file.write("SHA1:\n")
            for res in results[1]:
                report_file.write("{} - {}\n".format(res.get_name().strip(), res.get_sha1()))
        if not results[2] == [] and not args.sha256file == "None":
            report_file.write("SHA256:\n")
            for res in results[2]:
                report_file.write("{} - {}\n".format(res.get_name().strip(), res.get_sha256()))
    report_file.write("\n################\n")
    report_file.write("FILE INFORMATION\n")
    report_file.write("################\n")
    report_file.write("Regular Files Processed: {}\n".format(len(file_list)))
    if args.drive:
        for entry in file_list:
            report_file.write("{}\n".format(entry['title']))
    elif args.dropbox:
        for entry in file_list:
            report_file.write("{}\n".format(entry.name))
    report_file.write("\nDeleted Files Processed: {}\n".format(len(deleted_file_list)))
    if args.drive:
        for entry in deleted_file_list:
            report_file.write("{}\n".format(entry['title']))
    elif args.dropbox:
        for entry in deleted_file_list:
            report_file.write("{}\n".format(entry.name))
    report_file.write("\n#############\n")
    report_file.write("END OF REPORT\n")
    report_file.write("#############\n")

# Main function for generating the report
def generate_report(results, folder_name, args, timestamp, run_time, file_list, deleted_file_list):
    write_to_report_file(results, folder_name, args, timestamp, run_time, file_list, deleted_file_list)
