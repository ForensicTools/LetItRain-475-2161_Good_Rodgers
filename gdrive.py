# This file contains functions that use API calls for Google Drive
# to aggregate data

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import httplib2
import json
import os
import hashlib
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload
import io

def log_and_print(log_file, log_entry, newline=True):
    if newline:
        log_file.write(log_entry + "\n")
        print(log_entry)
    else:
        log_file.write(log_entry)
        print(log_entry, end="", flush=True)

# Handles authentication
def auth():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("letitrain-creds-gdrive.txt")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("letitrain-creds-gdrive.txt")
    httpauth = gauth.Get_Http_Object()
    service = discovery.build('drive', 'v3', http=httpauth)
    return gauth, httpauth, service

# Retrieves the information about every file
# Can either do deleted or regular files
def list_files(gauth, deleted, log_file):
    drive = GoogleDrive(gauth)
    if deleted:
        log_and_print(log_file, "Retrieving list of deleted files... ", False)
        file_list = drive.ListFile({'q': 'trashed=true'}).GetList()
        log_and_print(log_file, "Done!")
    else:
        log_and_print(log_file, "Retrieving list of regular files... ", False)
        file_list = drive.ListFile({'q': 'trashed=false'}).GetList()
        log_and_print(log_file, "Done!")
    return file_list

# makes the hashmap that determines file type to download when file is a
# Google-apps file
def make_hash_map():
    file1 = open('google_file_types.txt', 'r')
    file_types = dict()
    for line in file1:
        attribute_list = line.strip().split(',')
        file_types[attribute_list[0]] = [attribute_list[1], attribute_list[2]]
    return file_types

# Retrieves version information in JSON format of previous versions
# given a file ID
def download_revisions(httpauth, service, fileID, title, path, counter, log_file):
    if not os.path.exists(path + "/" + title):
        os.makedirs(path + "/" + title)
    url = "https://www.googleapis.com/drive/v3/files/" + fileID + "/revisions"
    resp, content = httpauth.request(url, 'GET')
    revisions = json.loads(content.decode('utf-8'))
    revision_info = []
    rev_num = 1
    for revision in revisions["revisions"]:
        revision_info.append([str(rev_num), revision["id"], revision["modifiedTime"]])
        file_path = path + "/" + title + "/" + title + ".rev" + str(rev_num)
        orig_title = str(title)
        # to prevent duplicate file names being saved
        if os.path.exists(file_path):
            file_path, title = get_new_file_name(file_path)
            log_and_print(log_file, counter + " File named '" + orig_title + "' already exists. Saving as '" + title + "' instead.")
        log_and_print(log_file, counter + " Downloading '" + title + ".rev" + str(rev_num) + "'...")
        request = service.revisions().get_media(fileId=fileID, revisionId=revision["id"])
        fh = io.FileIO(file_path, mode='wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("%d%%\r" % int(status.progress() * 100), end="", flush=True)
        log_and_print(log_file, counter + " Hashing '" + title + ".rev" + str(rev_num) + "'...")
        with open(path + "/_hashes.txt", "a") as hashes_file:
            hashes_file.write(title + ".rev" + str(rev_num) + "\n")
            hashes_file.write("--MD5: " + hash_file(file_path, "md5") + "\n")
            hashes_file.write("--SHA1: " + hash_file(file_path, "sha1") + "\n")
            hashes_file.write("--SHA256: " + hash_file(file_path, "sha256") + "\n")
        rev_num += 1
    log_and_print(log_file, counter + " Writing revision info for '" + title + "'...")
    with open(path + "/" + title + "/" + title + "_revisions.txt", "w") as saved_file:
        for item in revision_info:
            saved_file.write("Revision Number: " + item[0] + "\n")
            saved_file.write("--Revision ID: " + item[1] + "\n")
            saved_file.write("--Revision Last Modifed: " + item[2] + "\n")

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

# sanitizes name to remove invalid characters
def sanitize_name(name):
    name = name.replace('/', '_')
    name = name.replace(':', '_')
    name = name.replace('*', '_')
    name = name.replace('?', '_')
    name = name.replace('\\', '_')
    name = name.replace('|', '_')
    name = name.replace('<', '_')
    name = name.replace('"', '_')
    name = name.replace('.', '_')
    new_name = name.replace('>', '_')
    return new_name

# Download files from drive when given the fileID
def download_files(gauth, httpauth, service, file_list, path, log_file):
    total = len(file_list)
    progress = 0
    drive = GoogleDrive(gauth)
    gdrive_file_type = make_hash_map()
    for down_file in file_list:
        counter = "[" + str(progress).zfill(len(str(total))) + "/" + str(total) + "]"
        if check_revisions(httpauth, down_file['id']):
            if 'google-apps' in down_file['mimeType']:
                if not export_to_file(down_file, gdrive_file_type, httpauth, service, path, counter, log_file):
                    file_list.remove(down_file)
            else:
                download_revisions(httpauth, service, down_file['id'], down_file['title'], path, counter, log_file)
        else:
            if 'google-apps' in down_file['mimeType']:
                if not export_to_file(down_file, gdrive_file_type, httpauth, service, path, counter, log_file):
                    file_list.remove(down_file)
            else:
                title = down_file['title']
                file_path = path + "/" + title
                # to prevent duplicate file names being saved
                if os.path.exists(file_path):
                    file_path, title = get_new_file_name(file_path)
                    log_and_print(log_file, counter + " File named '" + down_file['title'] + "' already exists. Saving as '" + title + "' instead.")
                log_and_print(log_file, counter + " Downloading '" + title + "'...")
                request = service.files().get_media(fileId=down_file['id'])
                fh = io.FileIO(file_path, mode='wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print("%d%%\r" % int(status.progress() * 100), end="", flush=True)
                log_and_print(log_file, counter + " Hashing '" + title + "'...")
                with open(path + "/_hashes.txt", "a") as hashes_file:
                    hashes_file.write(title + "\n")
                    hashes_file.write("--MD5: " + hash_file(file_path, "md5") + "\n")
                    hashes_file.write("--SHA1: " + hash_file(file_path, "sha1") + "\n")
                    hashes_file.write("--SHA256: " + hash_file(file_path, "sha256") + "\n")
        progress += 1

def export_to_file(down_file, gdrive_file_type, httpauth, service, path, counter, log_file):
    value = gdrive_file_type[down_file['mimeType']]
    if value[0] != 'None':
        name = sanitize_name(down_file['title'])
        file_path = path + "/_google/" + name + value[0]
        # to prevent duplicate file names being saved
        if os.path.exists(file_path):
            file_path, name = get_new_file_name(file_path)
            name = name.split(".")[0]
            log_and_print(log_file, counter + " File named '" + down_file['title'] + "' already exists. Saving as '" + name + "' instead.")
            log_and_print(log_file, counter + " Downloading '" + name + "' as '" + name + value[0] + "'...")
        else:
            log_and_print(log_file, counter + " Downloading '" + name + "' as '" + name + value[0] + "'...")
        try:
            request = service.files().export_media(fileId=down_file['id'], mimeType=value[1])
            fh = io.FileIO(file_path, mode='wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("%d%%\r" % int(status.progress() * 100), end="", flush=True)
            log_and_print(log_file, counter + " Hashing '" + name + value[0] + "'...")
            with open(path + "/_google/_hashes.txt", "a") as hashes_file:
                hashes_file.write(name + value[0] + "\n")
                hashes_file.write("--MD5: " + hash_file(file_path, "md5") + "\n")
                hashes_file.write("--SHA1: " + hash_file(file_path, "sha1") + "\n")
                hashes_file.write("--SHA256: " + hash_file(file_path, "sha256") + "\n")
            return True
        except:
            log_and_print(log_file, "Failed to download '" + name + "'. The user most likely doesn't have permissions to export this file.")

    else:
        log_and_print(log_file, counter + " Skipping '" + down_file['title'] + "' because it is an unsupported MIME type.")

# if there is already a file being saved that has the name of the current file
# being created, this will return a new unique file name
def get_new_file_name(file_path):
    file_count = 1
    if "." in file_path:
        file_beginning, extension = file_path.split('.')
        while os.path.exists(file_beginning + str(file_count) + "." + extension):
            file_count = file_count + 1
        new_file_path = file_beginning + str(file_count) + "." + extension
        file_name = file_beginning.split('/')
        title = file_name[-1] + str(file_count) + "." + extension
    else:
        while os.path.exists(file_path + str(file_count)):
            file_count = file_count + 1
        new_file_path = file_path + str(file_count)
        file_name = file_path.split('/')
        title = file_name[-1] + str(file_count)
    return new_file_path, title

def hash_file(filename, alg):
    # Hashes a file with a given algorithm and returns the hash value
    blsize = 65536
    if alg == "md5":
        hasher = hashlib.md5()
    elif alg == "sha1":
        hasher = hashlib.sha1()
    elif alg == "sha256":
        hasher = hashlib.sha256()
    with open(filename, "rb") as hashfile:
        buf = hashfile.read(blsize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = hashfile.read(blsize)
    return hasher.hexdigest()

def create_dirs(timestamp):
    if not os.path.exists("gdrive_dump_{}".format(timestamp)):
        os.makedirs("gdrive_dump_{}".format(timestamp))
    if not os.path.exists("gdrive_dump_{}/regular".format(timestamp)):
        os.makedirs("gdrive_dump_{}/regular".format(timestamp))
    if not os.path.exists("gdrive_dump_{}/deleted".format(timestamp)):
        os.makedirs("gdrive_dump_{}/deleted".format(timestamp))
    regular_dir = "gdrive_dump_{}/regular".format(timestamp)
    deleted_dir = "gdrive_dump_{}/deleted".format(timestamp)
    if not os.path.exists("{}/_google".format(regular_dir)):
        os.makedirs("{}/_google".format(regular_dir))
    if not os.path.exists("{}/_google".format(deleted_dir)):
        os.makedirs("{}/_google".format(deleted_dir))
    return regular_dir, deleted_dir

def google_drive(timestamp, log_file):
    gauth, httpauth, service = auth()
    log_and_print(log_file, "Sucessfully authenticated to Google Drive.")
    log_and_print(log_file, "Creating directories... ", False)
    regular_dir, deleted_dir = create_dirs(timestamp)
    log_and_print(log_file, "Done!")
    file_list = list_files(gauth, False, log_file)
    log_and_print(log_file, "Downloading all regular files into '" + regular_dir + "'...")
    download_files(gauth, httpauth, service, file_list, regular_dir, log_file)
    log_and_print(log_file, "Done!")
    deleted_file_list = list_files(gauth, True, log_file)
    log_and_print(log_file, "Downloading all deleted files into '" + deleted_dir + "'...")
    download_files(gauth, httpauth, service, deleted_file_list, deleted_dir, log_file)
    log_and_print(log_file, "Done!")
    return "gdrive_dump_" + timestamp, file_list, deleted_file_list
