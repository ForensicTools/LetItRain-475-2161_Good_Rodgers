# This file contains functions that use API calls for Google Drive
# to aggregate data

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import httplib2
import json
import datetime
import os

# Handles authentication
def auth():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("letitrain-credentials.json")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("letitrain-credentials.json")
    httpauth = gauth.Get_Http_Object()
    return gauth, httpauth

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
def download_revisions(httpauth, fileID, title, path):
    if not os.path.exists(path + "/" + title):
        os.makedirs(path + "/" + title)
    url = "https://www.googleapis.com/drive/v3/files/" + fileID + "/revisions"
    resp, content = httpauth.request(url, 'GET')
    revisions = json.loads(content.decode('utf-8'))
    revision_info = []
    rev_num = 1
    for revision in revisions["revisions"]:
        revision_info.append([str(rev_num), revision["id"], revision["modifiedTime"]])
        url2 = url + "/" + revision["id"] + "?alt=media"
        response, content = httpauth.request(url2, 'GET')
        with open(path + "/" + title + "/" + title + ".rev" + str(rev_num), "wb") as saved_file:
            saved_file.write(content)
        rev_num += 1
    with open(path + "/" + title + "/" + title + "_revisions.txt", "w") as saved_file:
        for item in revision_info:
            saved_file.write("Revision Number: " + item[0] + "\n")
            saved_file.write("----Revision ID: " + item[1] + "\n")
            saved_file.write("----Revision Last Modifed: " + item[2] + "\n")

def check_revisions(gauth, fileID):
    httpauth = gauth
    url = "https://www.googleapis.com/drive/v3/files/" + fileID + "/revisions"
    resp, content = httpauth.request(url, 'GET')
    revisions = json.loads(content.decode('utf-8'))
    try:
        if len(revisions["revisions"]) > 1:
            return True
    except:
        return False

# Download files from drive when given the fileID
def download_files(gauth, httpauth, file_list, path):
    drive = GoogleDrive(gauth)
    for down_file in file_list:
        if check_revisions(httpauth, down_file['id']):
            if 'google-apps' in down_file['mimeType']:
                print("Google Apps Document")
            else:
                download_revisions(httpauth, down_file['id'], down_file['title'], path)
        else:
            if 'google-apps' in down_file['mimeType']:
                print("Google Apps Document")
            else:
                print("Downloading " + down_file['title'] + "...")
                url = "https://www.googleapis.com/drive/v3/files/{}?alt=media".format(down_file['id'])
                response, content = httpauth.request(url, 'GET')
                print(down_file['title'])
                with open(path + "/" + down_file['title'], "wb") as saved_file:
                    saved_file.write(content)

def create_dirs(timestamp):
    if not os.path.exists("gdrive_dump_{}".format(timestamp)):
        os.makedirs("gdrive_dump_{}".format(timestamp))
    if not os.path.exists("gdrive_dump_{}/regular".format(timestamp)):
        os.makedirs("gdrive_dump_{}/regular".format(timestamp))
    if not os.path.exists("gdrive_dump_{}/deleted".format(timestamp)):
        os.makedirs("gdrive_dump_{}/deleted".format(timestamp))
    regular_dir = "gdrive_dump_{}/regular".format(timestamp)
    deleted_dir = "gdrive_dump_{}/deleted".format(timestamp)
    return regular_dir, deleted_dir

def main():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
    regular_dir, deleted_dir = create_dirs(timestamp)
    gauth, httpauth = auth()
    file_list = list_files(gauth, False)
    trashed_file_list = list_files(gauth, True)
    download_files(gauth, httpauth, file_list, regular_dir)
    download_files(gauth, httpauth, trashed_file_list, deleted_dir)

if __name__ == '__main__':
    main()
