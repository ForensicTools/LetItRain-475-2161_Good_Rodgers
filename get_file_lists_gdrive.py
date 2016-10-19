# This file contains functions that use API calls for Google Drive
# to aggregate data

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Handles authentication
def auth():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
    return gauth

# Retrieves the information about every file
# Can either do deleted or regular files
def list_files(gauth, trashed):
    drive = GoogleDrive(gauth)
    if trashed:
        print("Retrieving list of deleted files...")
        file_list = drive.ListFile({'q': 'trashed=true'}).GetList()
    else:
        print("Retrieving list of regular files...")
        file_list = drive.ListFile({'q': 'trashed=false'}).GetList()
    return file_list

# Retrieves version information in JSON format of previous versions
# given a file ID
def get_file_versions(fileID, gauth):
    http = gauth[1]
    url = "https://www.googleapis.com/drive/v3/files/" + fileID + "/revisions"
    req = http.request(url, 'GET')

    print req[1]
    res = json.loads(req[1])
    print "\n\n" + res["revisions"][0]["id"]
    print len(res["revisions"])

# Download files from drive
# TODO

def main():
    output_file = open('file_list.txt', 'w')
    trashed_output_file = open('trashed_file_list.txt', 'w')
    gauth = auth()
    file_list = list_files(gauth, False)
    trashed_file_list = list_files(gauth, True)
    for file_entry in file_list:
        output_file.write("{}\n".format(file_entry['title']))
    print("List of regular files has been saved as file_list.txt")
    for file_entry in trashed_file_list:
        trashed_output_file.write("{}\n".format(file_entry['title']))
    print("List of deleted files has been saved as trashed_file_list.txt")
    print("Done!")

if __name__ == '__main__':
    main()
