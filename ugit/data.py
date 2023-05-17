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


def iter_refs():
    refs = ["HEAD"]
    for root, _dirnames, filenames in os.walk((GIT_DIR / "refs")):
        root = os.path.relpath(root, GIT_DIR).replace("\\", "/")
        refs.extend(f"{root}/{filename}/" for filename in filenames)

    # Yeild name, oid pairs
    for refname in refs:
        yield refname, get_ref(refname)


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
    ref_path = GIT_DIR / ref
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)

    ref_path.write_text(oid)


def get_ref(ref):
    # Refs can be either direct references to a commit or
    # symbolic references to another ref
    # Symbolic refs are in the format: "ref: {ref}"
    # Direct refs simply contain the oid of the commit

    ref_path = GIT_DIR / ref
    value = None

    if os.path.isfile(ref_path):
        value = ref_path.read_text().strip()

    if value and value.startwith("ref:"):
        return get_ref(value.split(":", 1)[1].strip())
