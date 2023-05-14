import os
import pathlib

from . import data


def write_tree(directory="."):
    entries = []
    for entry in pathlib.Path(directory).iterdir():
        if is_ignored(entry):
            continue
        if entry.is_file() and not entry.is_symlink():
            type_ = "blob"
            with open(entry, "rb") as f:
                oid = data.hash_object(f.read())

        elif entry.is_dir() and not entry.is_symlink():
            type_ = "tree"
            oid = write_tree(entry)

        entries.append((entry, oid, type_))

    tree = "".join(f"{type_} {oid} {name}\n" for name, oid, type_ in sorted(entries))
    print(tree)

    return data.hash_object(tree.encode(), "tree")


def is_ignored(path):
    ignore_dirs = [".git", ".ugit", "ugit.egg-info", "__pycache__"]
    path_parts = pathlib.Path(path).parts
    for igd in ignore_dirs:
        if igd in path_parts:
            return True
    return False


def _iter_tree_entries(oid):
    if not oid:
        return
    tree = data.get_object(oid, "tree")
    for entry in tree.decode().splitlines():
        type_, oid, name = entry.split(" ", 2)
        yield (type_, oid, name)


def get_tree(oid, base_path=""):
    result = {}
    for type_, oid, name in _iter_tree_entries(oid):
        if name in ["/", ".", ".."]:
            raise AssertionError(f"/, ., .., in path {name}")

        path = pathlib.Path(base_path, name)

        if type_ == "blob":
            result[path] = oid
        elif type_ == "tree":
            result.update(get_tree(oid, f"{path}/"))
        else:
            raise ValueError(f"Unknown type {type_}")
    return result


def read_tree(tree_oid):
    for path, oid in get_tree(tree_oid, base_path="./").items():
        os.makedirs(path, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data.get_object(oid=oid))
