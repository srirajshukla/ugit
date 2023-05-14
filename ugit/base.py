import pathlib

from . import data


def write_tree(directory="."):
    for entry in pathlib.Path(directory).iterdir():
        if entry.is_file() and not entry.is_symlink():
            if is_ignored(entry):
                continue
            print(entry)
            # TODO: create the oid by writing to object store
        elif entry.is_dir() and not entry.is_symlink():
            write_tree(entry)

    # TODO: create the object tree


def is_ignored(path):
    ignore_dirs = [".git", ".ugit", "ugit.egg-info", "__pycache__"]
    path_parts = pathlib.Path(path).parts
    for igd in ignore_dirs:
        if igd in path_parts:
            return True
    return False
