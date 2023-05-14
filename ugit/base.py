import pathlib

from . import data


def write_tree(directory="."):
    for entry in pathlib.Path(directory).iterdir():
        if entry.is_file() and not entry.is_symlink():
            print(entry)
            # TODO: create the oid by writing to object store
        elif entry.is_dir() and not entry.is_symlink():
            write_tree(entry)

    # TODO: create the object tree
