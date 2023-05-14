import os
import hashlib

GIT_DIR = ".ugit"


def init():
    try:
        os.makedirs(GIT_DIR)
        os.makedirs(f"{GIT_DIR}/objects")
        return True
    except OSError as e:
        return False


def hash_object(data):
    oid = hashlib.sha1(data).hexdigest()
    with open(f"{GIT_DIR}/objects/{oid}", "wb") as f:
        f.write(data)
    return oid


def get_object(oid):
    with open(f"{GIT_DIR}/objects/{oid}", "rb") as f:
        return f.read()
