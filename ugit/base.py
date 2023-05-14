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
