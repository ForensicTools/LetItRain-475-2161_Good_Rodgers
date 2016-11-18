# Contains report generation code

import os
from file_object import FileObject

def log_and_print(log_file, log_entry):
    log_file.write(log_entry + "\n")
    print(log_entry)

# Write to the txt file the hashing results
def write_to_report_file(results, folder_name, args, timestamp, run_time, file_list, deleted_file_list):
    report_file = open("{}/report.txt".format(folder_name), 'w')
    report_file.write("#######################################\n")
    report_file.write("############## LetItRain ##############\n")
    report_file.write("#######################################\n\n")
    report_file.write("###############\n")
    report_file.write("RUN INFORMATION\n")
    report_file.write("###############\n")
    report_file.write("Folder name: {}\n".format(folder_name))
    report_file.write("Time started: {}\n".format(timestamp))
    report_file.write("Total run time: {}\n\n".format(run_time))
    report_file.write("###################\n")
    report_file.write("HASHING INFORMATION\n")
    report_file.write("###################\n")
    if args.positive:
        report_file.write("Positive Hashing Matches:\n")
        hash_matching_performed = True
    elif args.negative:
        report_file.write("Negative Hashing Matches:\n")
        hash_matching_performed = True
    else:
        report_file.write("No hash matching requested.\n\n")
        hash_matching_performed = False
    if hash_matching_performed:
        if not results[0] == [] and not args.md5file == "None":
            report_file.write("\n\nMD5:\n")
            for res in results[0]:
                report_file.write("{} - {}\n".format(res.get_name().strip(), res.get_md5()))
        if not results[1] == [] and not args.sha1file == "None":
            report_file.write("\n\nSHA1:\n")
            for res in results[1]:
                report_file.write("{} - {}\n".format(res.get_name().strip(), res.get_sha1()))
        if not results[2] == [] and not args.sha256file == "None":
            report_file.write("\n\nSHA256:\n")
            for res in results[2]:
                report_file.write("{} - {}\n".format(res.get_name().strip(), res.get_sha256()))
    report_file.write("################\n")
    report_file.write("FILE INFORMATION\n")
    report_file.write("################\n")
    report_file.write("Regular Files Processed: {}\n".format(len(file_list)))
    for entry in file_list:
        report_file.write("{}\n".format(entry.name))
    report_file.write("\nDeleted Files Processed: {}\n".format(len(deleted_file_list)))
    for entry in deleted_file_list:
        report_file.write("{}\n".format(entry.name))

# Main function for generating the report
def generate_report(log_file, results, folder_name, args, timestamp, run_time, file_list, deleted_file_list):
    write_to_report_file(results, folder_name, args, timestamp, run_time, file_list, deleted_file_list)
