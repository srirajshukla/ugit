import os
import pathlib
import itertools
import operator
from collections import namedtuple

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

        entries.append((entry.name, oid, type_))

    tree = "".join(f"{type_} {oid} {name}\n" for name, oid, type_ in sorted(entries))
    print(tree)

    return data.hash_object(tree.encode(), "tree")


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
            result.update(get_tree(oid, f"{path}"))
        else:
            raise ValueError(f"Unknown type {type_}")
    return result


def _empty_current_directory():
    for root, dirnames, filenames in os.walk(".", topdown=False):
        for filename in filenames:
            path = pathlib.Path(root, filename)
            if is_ignored(path) or not os.path.isfile(path):
                continue
            os.remove(path)

        for dirname in dirnames:
            path = pathlib.Path(root, dirname)
            if is_ignored(path):
                continue
            try:
                os.rmdir(path)
            except (FileNotFoundError, OSError) as e:
                pass


def read_tree(tree_oid):
    _empty_current_directory()
    for path, oid in get_tree(tree_oid, base_path="./").items():
        path_root = os.path.dirname(path)
        if path_root != "":
            os.makedirs(path_root, exist_ok=True)

        with open(path, "wb") as f:
            f.write(data.get_object(oid=oid))


def commit(message):
    commit_m = f"tree {write_tree()}\n"

    HEAD = data.get_ref("HEAD")
    if HEAD:
        commit_m += f"parent {HEAD}\n"

    commit_m += f"\n{message}\n"

    oid = data.hash_object(commit_m.encode(), type_="commit")
    data.update_ref("HEAD", oid)

    return oid


def checkout(oid):
    commit: Commit = get_commit(oid)
    read_tree(commit.tree)
    data.update_ref("HEAD", oid)


Commit = namedtuple("Commit", ["tree", "parent", "message"])


def get_commit(oid):
    parent = None

    commit = data.get_object(oid, "commit").decode()
    lines = iter(commit.splitlines())

    for line in itertools.takewhile(operator.truth, lines):
        key, value = line.split(" ", 1)
        if key == "tree":
            tree = value
        elif key == "parent":
            parent = value
        else:
            raise ValueError(f"Unknown field {key}")

    message = "\n".join(lines)
    return Commit(tree=tree, parent=parent, message=message)


def is_ignored(path):
    ignore_dirs = [".git", ".ugit", "ugit.egg-info", "__pycache__"]
    path_parts = pathlib.Path(path).parts
    for igd in ignore_dirs:
        if igd in path_parts:
            return True
    return False
