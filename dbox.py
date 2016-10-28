import dropbox
import datetime
import os
import hashlib

def auth():
    dbx = dropbox.Dropbox('')
    return dbx

def list_files(dbx):
    file_list = dbx.files_list_folder('', recursive=True).entries
    return file_list

def check_revisions(dbx, file_entry):
    revisions = dbx.files_list_revisions(file_entry.path_lower)
    if len(revisions.entries) > 1:
        return revisions

def download_revisions(dbx, revisions, path, counter, file_name):
    if not os.path.exists(path + "/" + file_name):
        os.makedirs(path + "/" + file_name)
    revision_info = []
    rev_num = 1
    for revision in revisions.entries:
        file_entry = revision
        revision_info.append([str(rev_num), file_entry.rev, file_entry.client_modified])
        print(counter + " Downloading '" + file_entry.name + ".rev" + str(rev_num) + "'...")
        file_path = path + "/" + file_name + "/" + file_entry.name + ".rev" + str(rev_num)
        dbx.files_download_to_file(file_path, file_entry.id)
        print(counter + " Hashing '" + file_entry.name + "'...")
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

def download_files(dbx, file_list, path):
    total = len(file_list)
    progress = 1
    for file_entry in file_list:
        counter = "[" + str(progress).zfill(len(str(total))) + "/" + str(total) + "]"
        if str(file_entry)[:6] != "Folder":
            revisions = check_revisions(dbx, file_entry)
            if revisions:
                    download_revisions(dbx, revisions, path, counter, file_entry.name)
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
            print(counter + " Skipping " + file_entry.name + " because it is a directory.")
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
    if not os.path.exists("{}/_dropbox".format(regular_dir)):
        os.makedirs("{}/_dropbox".format(regular_dir))
    if not os.path.exists("{}/_dropbox".format(deleted_dir)):
        os.makedirs("{}/_dropbox".format(deleted_dir))
    return regular_dir, deleted_dir

def main():
    dbx = auth()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
    print("Creating directories...")
    regular_dir, deleted_dir = create_dirs(timestamp)
    print("Done!")
    file_list = list_files(dbx)
    print("Downloading all regular files into '" + regular_dir + "' ...")
    download_files(dbx, file_list, regular_dir)
    print("Done!")
    print("Exiting...")

if __name__ == '__main__':
    main()
