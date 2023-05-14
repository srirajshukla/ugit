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


def hash_object(data, type_="blob"):
    obj = type_.encode() + b"\x00" + data
    oid = hashlib.sha1(obj).hexdigest()

    with open(f"{GIT_DIR}/objects/{oid}", "wb") as f:
        f.write(obj)

    return oid


def get_object(oid, expected_type=None):
    with open(f"{GIT_DIR}/objects/{oid}", "rb") as f:
        obj = f.read()

    type_, _, content = obj.partition(b"\x00")
    type_ = type_.decode()

    if expected_type is not None and type_ != expected_type:
        raise ValueError(f"Expected {expected_type} got {type_}")

    return content
