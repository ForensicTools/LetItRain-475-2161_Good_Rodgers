import dropbox
import os
import hashlib
import sys

# Print something to the console and log it to the log file
def log_and_print(log_file, log_entry):
    log_file.write(log_entry + "\n")
    print(log_entry)

# Authenticate with Dropbox and save the access token for future runs
def auth(log_file):
    if os.path.exists("letitrain-creds-dbox.txt"):
        with open("letitrain-creds-dbox.txt", "r") as creds_file:
            access_token = creds_file.readline().strip()
            if not access_token:
                log_and_print(log_file, "Credentials file doesn't contain a key.")
                access_token = gen_access_token(log_file)
    else:
        access_token = gen_access_token(log_file)
    dbx = dropbox.Dropbox(access_token)
    try:
        dbx.users_get_current_account()
    except:
        return False
    return dbx

# Generate the access token for the Dropbox app to interrogate the account
def gen_access_token(log_file):
    app_key = input("Enter the app key for the Dropbox app: ").strip()
    app_secret = input("Enter the app secret for the Dropbox app: ").strip()
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
    authorize_url = flow.start()
    log_and_print(log_file, "1. Go to: " + authorize_url)
    log_and_print(log_file, "2. Click 'Allow' (you might have to log in first)")
    code = input("3. Enter the authorization code that you are given here: ").strip()
    access_token, user_id = flow.finish(code)
    with open("letitrain-creds-dbox.txt", "w") as creds_file:
        creds_file.write(access_token)
    return access_token

# List all files in the Dropbox account
# Can return both regular files and deleted files
# Deleted files have to be checked one by one to see if it can be restored
def list_files(dbx, deleted, log_file):
    file_list = []
    if deleted:
        log_and_print(log_file, "Retrieving list of deleted files...")
        dbx_list = dbx.files_list_folder('', recursive=True, include_deleted=True)
        for entry in dbx_list.entries:
            if isinstance(entry, dropbox.files.DeletedMetadata):
                log_and_print(log_file, "Checking if '" + entry.path_display + "' can be restored...")
                try:
                    revisions = dbx.files_list_revisions(entry.path_lower)
                    if len(revisions.entries) > 0:
                        log_and_print(log_file, entry.path_display + "' can be restored. Adding it to the list of files to restore.")
                        file_list.append(entry)
                except:
                    pass
        while dbx_list.has_more:
            for entry in dbx_list.entries:
                if isinstance(entry, dropbox.files.DeletedMetadata):
                    try:
                        revisions = dbx.files_list_revisions(entry.path_lower)
                        if len(revisions.entries) > 0:
                            file_list.append(entry)
                    except:
                        pass
    else:
        log_and_print(log_file, "Retrieving list of regular files...")
        dbx_list = dbx.files_list_folder('', recursive=True)
        file_list = dbx_list.entries
        while dbx_list.has_more:
            dbx.files_list_folder_continue(dbx_list.cursor)
            for entry in dbx_list.entries:
                file_list.append(entry)
    return file_list


# Check if there are any revisions for a given file
def check_revisions(dbx, file_entry):
    revisions = dbx.files_list_revisions(file_entry.path_lower)
    if len(revisions.entries) > 1:
        return revisions

# Download all available revisions for a given file and write the revision information to a file
def download_revisions(dbx, revisions, path, counter, file_name, deleted, log_file):
    if not os.path.exists(path + "/" + file_name):
        os.makedirs(path + "/" + file_name)
    revision_info = []
    rev_num = 1
    for revision in revisions.entries:
        file_entry = revision
        revision_info.append([str(rev_num), file_entry.rev, file_entry.client_modified])
        file_path = path + "/" + file_name + "/" + file_entry.name + ".rev" + str(rev_num)
        if deleted:
            log_and_print(log_file, counter + " Restoring revision '" + file_entry.name + ".rev" + str(rev_num) + "' in Dropbox...")
            dbx.files_restore(file_entry.path_lower, file_entry.rev)
            log_and_print(log_file, counter + " Downloading revision '" + file_entry.rev + "' of '" + file_entry.name + "' as '" + file_entry.name + ".rev" + str(rev_num) + "'...")
            dbx.files_download_to_file(file_path, file_entry.path_lower)
            log_and_print(log_file, counter + " Deleting '" + file_entry.name + ".rev" + str(rev_num) + "' in Dropbox...")
            dbx.files_delete(file_entry.path_lower)
        else:
            log_and_print(log_file, counter + " Downloading revision '" + file_entry.rev + "' of '" + file_entry.name + "' as '" + file_entry.name + ".rev" + str(rev_num) + "'...")
            dbx.files_download_to_file(file_path, file_entry.id)
        log_and_print(log_file, counter + " Hashing '" + file_entry.name + ".rev" + str(rev_num) + "'...")
        with open(path + "/_hashes.txt", "a") as hashes_file:
            hashes_file.write(file_entry.name + ".rev" + str(rev_num) + "\n")
            hashes_file.write("--MD5: " + hash_file(file_path, "md5") + "\n")
            hashes_file.write("--SHA1: " + hash_file(file_path, "sha1") + "\n")
            hashes_file.write("--SHA256: " + hash_file(file_path, "sha256") + "\n")
        rev_num += 1
    log_and_print(log_file, counter + " Writing revision info for '" + file_name + "'...")
    with open(path + "/" + file_name + "/" + file_name + "_revisions.txt", "w") as saved_file:
        for item in revision_info:
            saved_file.write("Revision Number: " + item[0] + "\n")
            saved_file.write("--Revision ID: " + item[1] + "\n")
            saved_file.write("--Revision Last Modifed: " + str(item[2]) + "\n")

# Download all files in the Dropbox account and perform hashing on each one
# Can either download regular files or deleted files that can still be restored
def download_files(dbx, file_list, path, deleted, log_file):
    total = len(file_list)
    progress = 1
    if deleted:
        for file_entry in file_list:
            counter = "[" + str(progress).zfill(len(str(total))) + "/" + str(total) + "]"
            revisions = check_revisions(dbx, file_entry)
            if revisions:
                download_revisions(dbx, revisions, path, counter, file_entry.name, True, log_file)
            else:
                file_revision = dbx.files_list_revisions(file_entry.path_lower).entries[0]
                file_path = path + "/" + file_entry.name
                log_and_print(log_file, counter + " Restoring '" + file_entry.name + "' in Dropbox...")
                dbx.files_restore(file_revision.path_lower, file_revision.rev)
                log_and_print(log_file, counter + " Downloading '" + file_entry.name + "'...")
                dbx.files_download_to_file(file_path, file_revision.path_lower)
                log_and_print(log_file, counter + " Deleting '" + file_entry.name + "' in Dropbox...")
                dbx.files_delete(file_revision.path_lower)
                log_and_print(log_file, counter + " Hashing '" + file_entry.name + "'...")
                with open(path + "/_hashes.txt", "a") as hashes_file:
                    hashes_file.write(file_entry.name + "\n")
                    hashes_file.write("--MD5: " + hash_file(file_path, "md5") + "\n")
                    hashes_file.write("--SHA1: " + hash_file(file_path, "sha1") + "\n")
                    hashes_file.write("--SHA256: " + hash_file(file_path, "sha256") + "\n")
            progress += 1
    else:
        for file_entry in file_list:
            counter = "[" + str(progress).zfill(len(str(total))) + "/" + str(total) + "]"
            if not isinstance(file_entry, dropbox.files.FolderMetadata):
                revisions = check_revisions(dbx, file_entry)
                if revisions:
                        download_revisions(dbx, revisions, path, counter, file_entry.name, False, log_file)
                else:
                    log_and_print(log_file, counter + " Downloading '" + file_entry.name + "'...")
                    file_path = path + "/" + file_entry.name
                    dbx.files_download_to_file(file_path, file_entry.id)
                    log_and_print(log_file, counter + " Hashing '" + file_entry.name + "'...")
                    with open(path + "/_hashes.txt", "a") as hashes_file:
                        hashes_file.write(file_entry.name + "\n")
                        hashes_file.write("--MD5: " + hash_file(file_path, "md5") + "\n")
                        hashes_file.write("--SHA1: " + hash_file(file_path, "sha1") + "\n")
                        hashes_file.write("--SHA256: " + hash_file(file_path, "sha256") + "\n")
            else:
                log_and_print(log_file, counter + " Skipping '" + file_entry.name + "' because it is a directory.")
                file_list.remove(file_entry)
            progress += 1

# Hash a given file in either SHA1, SHA256, or MD5
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

# Create the directories that the tool will store the downloded files and generated reports
def create_dirs(timestamp):
    if not os.path.exists("dbox_dump_{}".format(timestamp)):
        os.makedirs("dbox_dump_{}".format(timestamp))
    if not os.path.exists("dbox_dump_{}/regular".format(timestamp)):
        os.makedirs("dbox_dump_{}/regular".format(timestamp))
    if not os.path.exists("dbox_dump_{}/deleted".format(timestamp)):
        os.makedirs("dbox_dump_{}/deleted".format(timestamp))
    regular_dir = "dbox_dump_{}/regular".format(timestamp)
    deleted_dir = "dbox_dump_{}/deleted".format(timestamp)
    return regular_dir, deleted_dir

def dbox(timestamp, log_file):
    dbx = auth(log_file)
    if not dbx:
        log_and_print(log_file, "Could not authenticate to Dropbox. Please check your access token.")
        sys.exit()
    log_and_print(log_file, "Sucessfully authenticated to Dropbox.")
    print("Would you like to attempt to download deleted files and their revisions?")
    print("WARNING: THIS WILL MODIFY THE DELETED FILES IN DROPBOX")
    print("In order to download deleted files, they must first be restored in Dropbox.")
    print("After they are restored, they will be deleted again, adding a new revision to them.")
    print("This step may take a VERY LONG TIME if there are a lot of deleted files.")
    print("We have to check each one to see if it is still recoverable.")
    print("If you would like to continue downloading deleted files, please enter 'Yes, I am sure'")
    confirm = input("Otherwise, just hit enter: ")
    log_and_print(log_file, "Creating directories...")
    regular_dir, deleted_dir = create_dirs(timestamp)
    log_and_print(log_file, "Done!")
    file_list = list_files(dbx, False, log_file)
    log_and_print(log_file, "Downloading all regular files into '" + regular_dir + "' ...")
    download_files(dbx, file_list, regular_dir, False, log_file)
    log_and_print(log_file, "Done!")
    deleted_file_list = []
    if confirm == "Yes, I am sure":
        deleted_file_list = list_files(dbx, True, log_file)
        log_and_print(log_file, "Downloading all deleted files into '" + deleted_dir + "' ...")
        download_files(dbx, deleted_file_list, deleted_dir, True, log_file)
        log_and_print(log_file, "Done!")
    else:
        log_and_print(log_file, "Skipping deleted files.")
        log_and_print(log_file, "Done!")
    return "dbox_dump_" + timestamp, file_list, deleted_file_list
