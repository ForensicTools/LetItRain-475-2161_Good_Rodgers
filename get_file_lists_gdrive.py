# This file contains functions that use API calls for Google Drive
# to aggregate data

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import httplib2
import json

# Handles authentication
def auth():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
    http = gauth.Get_Http_Object()
    lst = [gauth, http]
    return lst


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
    http = gauth
    url = "https://www.googleapis.com/drive/v3/files/" + fileID + "/revisions"
    req = http.request(url, 'GET')
    res = json.loads(req[1])
    print("There are " + str(len(res["revisions"])) + " revisions for this file.")

    #fileID_for_revision will be the fileID of the revision in question
    url2 = url + "/" + fileID_for_revision + "?alt=media"
    response, content = http.request(url2, 'GET')
    with open("test.docx", "wb") as code:
        code.write(content)

# Download files from drive when given the fileID
def download_file(gauth, fileID):
    drive = GoogleDrive(gauth)
    file1 = drive.CreateFile({'id': fileID})
    mime = file1['mimeType']
    content = file1.GetContentFile(file1['title'])

def main():
    output_file = open('file_list.txt', 'w')
    trashed_output_file = open('trashed_file_list.txt', 'w')
    gauth = auth()
    file_list = list_files(gauth[0], False)
    trashed_file_list = list_files(gauth[0], True)
    for file_entry in file_list:
        output_file.write("{}\n".format(file_entry['title']))
    print("List of regular files has been saved as file_list.txt")
    for file_entry in trashed_file_list:
        trashed_output_file.write("{}\n".format(file_entry['title']))
    print("List of deleted files has been saved as trashed_file_list.txt")
    print("Done!")

if __name__ == '__main__':
    main()
