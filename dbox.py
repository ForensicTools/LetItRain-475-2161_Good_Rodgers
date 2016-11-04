import dropbox
import datetime
import os
import hashlib
import sys

def auth():
    if os.path.exists("letitrain-creds-dbox.txt"):
        with open("letitrain-creds-dbox.txt", "r") as creds_file:
            key = creds_file.readline().strip()
            if not key:
                print("Credentials file doesn't contain a key.")
                key = input("Enter your Dropbox access token: ")
                with open("letitrain-creds-dbox.txt", "w") as creds_file:
                    creds_file.write(key)
    else:
        key = input("Enter your Dropbox access token: ")
        with open("letitrain-creds-dbox.txt", "w") as creds_file:
            creds_file.write(key)
    dbx = dropbox.Dropbox(key)
    try:
        dbx.users_get_current_account()
    except:
        return False
    return dbx

def list_files(dbx, deleted):
    file_list = []
    if deleted:
        print("Retrieving list of deleted files...")
        dbx_list = dbx.files_list_folder('', recursive=False, include_deleted=True)
        for entry in dbx_list.entries:
            if isinstance(entry, dropbox.files.DeletedMetadata):
                try:
                    revisions = dbx.files_list_revisions(entry.path_lower)
                    if len(revisions.entries) > 0:
                        file_list.append(entry)
                except:
                    pass
        while dbx_list.has_more:
            for entry in dbx_list.entries:
                if isinstance(entry, dropbox.files.DeletedMetadata):
                    print(entry)
                    try:
                        revisions = dbx.files_list_revisions(entry.path_lower)
                        if len(revisions.entries) > 0:
                            file_list.append(entry)
                    except:
                        pass
    else:
        print("Retrieving list of regular files...")
        dbx_list = dbx.files_list_folder('', recursive=True)
        file_list = dbx_list.entries
        while dbx_list.has_more:
            dbx.files_list_folder_continue(dbx_list.cursor)
            for entry in dbx_list.entries:
                file_list.append(entry)
    return file_list

def check_revisions(dbx, file_entry):
    revisions = dbx.files_list_revisions(file_entry.path_lower)
    if len(revisions.entries) > 1:
        return revisions

def download_revisions(dbx, revisions, path, counter, file_name, deleted):
    if not os.path.exists(path + "/" + file_name):
        os.makedirs(path + "/" + file_name)
    revision_info = []
    rev_num = 1
    for revision in revisions.entries:
        file_entry = revision
        revision_info.append([str(rev_num), file_entry.rev, file_entry.client_modified])
        file_path = path + "/" + file_name + "/" + file_entry.name + ".rev" + str(rev_num)
        if deleted:
            print(counter + " Restoring revision'" + file_entry.name + ".rev" + str(rev_num) + "' in Dropbox...")
            dbx.files_restore(file_entry.path_lower, file_entry.rev)
            print(counter + " Downloading revision '" + file_entry.rev + "' of '" + file_entry.name + "' as '" + file_entry.name + ".rev" + str(rev_num) + "'...")
            dbx.files_download_to_file(file_path, file_entry.path_lower)
            print(counter + " Deleting '" + file_entry.name + ".rev" + str(rev_num) + "' in Dropbox...")
            dbx.files_delete(file_entry.path_lower)
        else:
            print(counter + " Downloading revision '" + file_entry.rev + "' of '" + file_entry.name + "' as '" + file_entry.name + ".rev" + str(rev_num) + "'...")
            dbx.files_download_to_file(file_path, file_entry.id)
        print(counter + " Hashing '" + file_entry.name + ".rev" + str(rev_num) + "'...")
        with open(path + "/_hashes.txt", "a") as hashes_file:
            hashes_file.write(file_entry.name + ".rev" + str(rev_num) + "\n")
            hashes_file.write("--MD5: " + hash_file(file_path, "md5") + "\n")
            hashes_file.write("--SHA1: " + hash_file(file_path, "sha1") + "\n")
            hashes_file.write("--SHA256: " + hash_file(file_path, "sha256") + "\n")
        rev_num += 1
    print(counter + " Writing revision info for '" + file_name + "'...")
    with open(path + "/" + file_name + "/" + file_name + "_revisions.txt", "w") as saved_file:
        for item in revision_info:
            saved_file.write("Revision Number: " + item[0] + "\n")
            saved_file.write("--Revision ID: " + item[1] + "\n")
            saved_file.write("--Revision Last Modifed: " + str(item[2]) + "\n")

def download_files(dbx, file_list, path, deleted):
    total = len(file_list)
    progress = 1
    if deleted:
        for file_entry in file_list:
            counter = "[" + str(progress).zfill(len(str(total))) + "/" + str(total) + "]"
            revisions = check_revisions(dbx, file_entry)
            if revisions:
                download_revisions(dbx, revisions, path, counter, file_entry.name, True)
            else:
                file_revision = dbx.files_list_revisions(file_entry.path_lower).entries[0]
                file_path = path + "/" + file_entry.name
                print(counter + " Restoring '" + file_entry.name + "' in Dropbox...")
                dbx.files_restore(file_revision.path_lower, file_revision.rev)
                print(counter + " Downloading '" + file_entry.name + "'...")
                dbx.files_download_to_file(file_path, file_revision.path_lower)
                print(counter + " Deleting '" + file_entry.name + "' in Dropbox...")
                dbx.files_delete(file_revision.path_lower)
                print(counter + " Hashing '" + file_entry.name + "'...")
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
                        download_revisions(dbx, revisions, path, counter, file_entry.name, False)
                else:
                    print(counter + " Downloading '" + file_entry.name + "'...")
                    file_path = path + "/" + file_entry.name
                    dbx.files_download_to_file(file_path, file_entry.id)
                    print(counter + " Hashing '" + file_entry.name + "'...")
                    with open(path + "/_hashes.txt", "a") as hashes_file:
                        hashes_file.write(file_entry.name + "\n")
                        hashes_file.write("--MD5: " + hash_file(file_path, "md5") + "\n")
                        hashes_file.write("--SHA1: " + hash_file(file_path, "sha1") + "\n")
                        hashes_file.write("--SHA256: " + hash_file(file_path, "sha256") + "\n")
            else:
                print(counter + " Skipping '" + file_entry.name + "' because it is a directory.")
            progress += 1

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
    if not os.path.exists("dbox_dump_{}".format(timestamp)):
        os.makedirs("dbox_dump_{}".format(timestamp))
    if not os.path.exists("dbox_dump_{}/regular".format(timestamp)):
        os.makedirs("dbox_dump_{}/regular".format(timestamp))
    if not os.path.exists("dbox_dump_{}/deleted".format(timestamp)):
        os.makedirs("dbox_dump_{}/deleted".format(timestamp))
    regular_dir = "dbox_dump_{}/regular".format(timestamp)
    deleted_dir = "dbox_dump_{}/deleted".format(timestamp)
    return regular_dir, deleted_dir

def main():
    dbx = auth()
    if not dbx:
        print("Could not authenticate to Dropbox. Please check your access token.")
        sys.exit()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
    print("Creating directories...")
    regular_dir, deleted_dir = create_dirs(timestamp)
    print("Done!")
    file_list = list_files(dbx, False)
    print("Downloading all regular files into '" + regular_dir + "' ...")
    download_files(dbx, file_list, regular_dir, False)
    print("Done!")
    print("Would you like to attempt to download deleted files and their revisions?")
    print("WARNING: THIS WILL MODIFY THE DELETED FILES IN DROPBOX")
    print("In order to download deleted files, they must first be restored in Dropbox.")
    print("After they are restored, they will be deleted again, adding a new revision to them.")
    print("This step may take a very long time if there are a lot of deleted files.")
    print("We have to check each one to see if it is still recoverable.")
    confirm = input("If you would like to continue downloading deleted files, please enter 'Yes, I am sure': ")
    if confirm == "Yes, I am sure":
        deleted_file_list = list_files(dbx, True)
        print("Downloading all deleted files into '" + deleted_dir + "' ...")
        download_files(dbx, deleted_file_list, deleted_dir, True)
        print("Done!")
    else:
        print("Skipping deleted files.")
    print("Exiting...")

if __name__ == '__main__':
    main()
