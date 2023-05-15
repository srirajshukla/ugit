import os
import hashlib
import pathlib

GIT_DIR = pathlib.Path(".ugit")


def init():
    try:
        GIT_DIR.mkdir(parents=True)
        (GIT_DIR / "objects").mkdir(parents=True)

        return True
    except OSError as e:
        return False


def hash_object(data, type_="blob"):
    obj = type_.encode() + b"\x00" + data
    oid = hashlib.sha1(obj).hexdigest()

    (GIT_DIR / "objects" / oid).write_bytes(obj)

    return oid


def get_object(oid, expected_type=None):
    obj = (GIT_DIR / "objects" / oid).read_bytes()

    type_, _, content = obj.partition(b"\x00")
    type_ = type_.decode()

    if expected_type is not None and type_ != expected_type:
        raise ValueError(f"Expected {expected_type} got {type_}")

    return content


def update_ref(ref, oid):
    ref_path = (GIT_DIR/ref)
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)

    ref_path.write_text(oid)


def get_ref(ref):
    ref_path = (GIT_DIR/ref)
    if os.path.isfile(ref_path):
        return ref_path.read_text().strip()
