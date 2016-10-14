# This file contains functions that use API calls for Google Drive
# to aggregate data

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive 

# Handles authentication
def auth():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
    return gauth

# Lists the names of all the files in the root directory
def list_files(gauth):
    drive = GoogleDrive(gauth)
    print("file list:\n\n")
    file_list = drive.ListFile({'q': "'root' in parents and trashed=true"}).GetList()
    for file in file_list:
        print(file['title'])

def main():
    gauth = auth()
    list_files(gauth)

main()

print("Done!")

