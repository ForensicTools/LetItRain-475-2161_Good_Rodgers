# Class for downloaded files objects. This has the name of the file, its corresponding
# hashes, and then whether or not it has a matching hash to a given hash list
class FileObject():
    def __init__(self):
        self.name = "None"
        self.md5 = "None"
        self.sha1 = "None"
        self.sha256 = "None"
        self.md5_match = False
        self.sha1_match = False
        self.sha256_match = False

    def set_name(self, name):
        self.name = name

    def set_md5(self, md5):
        self.md5 = md5

    def set_sha1(self, sha1):
        self.sha1 = sha1

    def set_sha256(self, sha256):
        self.sha256 = sha256

    def set_md5_hash_match(self, boolean):
        self.md5_match = boolean

    def set_md5_hash_match(self, boolean):
        self.md5_match = boolean

    def set_sha1_hash_match(self, boolean):
        self.sha1_match = boolean

    def set_sha256_hash_match(self, boolean):
        self.sha256_match = boolean

    def get_name(self):
        return self.name

    def get_md5(self):
        return self.md5

    def get_sha1(self):
        return self.sha1

    def get_sha256(self):
        return self.sha256

    def get_md5_match(self):
        return self.md5_match

    def get_sha1_match(self):
        return self.sha1_match

    def get_sha256_match(self):
        return self.sha256_match
