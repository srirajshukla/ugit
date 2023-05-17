import os
import pathlib
import itertools
import operator
from collections import namedtuple, deque
import string

from . import data


def init():
    created = data.init()
    if created:
        data.update_ref("HEAD", data.RefValue(symbolic=True, value="refs/heads/master"))
        return True
    else:
        return False


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

    HEAD = data.get_ref("HEAD").value
    if HEAD:
        commit_m += f"parent {HEAD}\n"

    commit_m += f"\n{message}\n"

    oid = data.hash_object(commit_m.encode(), type_="commit")
    data.update_ref("HEAD", data.RefValue(symbolic=False, value=oid))

    return oid


def checkout(name):
    oid = get_oid(name)
    commit: Commit = get_commit(oid)
    read_tree(commit.tree)

    if is_branch(name):
        HEAD = data.RefValue(symbolic=True, value=f"refs/heads/{name}")
    else:
        HEAD = data.RefValue(symbolic=False, value=oid)

    data.update_ref("HEAD", HEAD, deref=False)


def create_tag(name, oid):
    data.update_ref(f"refs/tags/{name}", data.RefValue(symbolic=False, value=oid))


def create_branch(name, oid):
    data.update_ref(f"refs/heads/{name}", data.RefValue(symbolic=False, value=oid))


def iter_branch_names():
    for refname, _ in data.iter_refs("refs/heads/"):
        yield os.path.relpath(refname, "refs/heads")


def is_branch(branch):
    return data.get_ref(f"refs/heads/{branch}").value is not None


def get_branch_name():
    HEAD = data.get_ref("HEAD", deref=False)
    if not HEAD.symbolic:
        return None

    HEAD = HEAD.value
    if not HEAD.startswith("refs/heads/"):
        raise ValueError(f"HEAD ref {HEAD} is not a branch")
    return os.path.relpath(HEAD, "refs/heads")


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


def iter_commits_and_parents(oids):
    oids = deque(oids)
    visited = set()

    while oids:
        oid = oids.popleft()
        if not oid or oid in visited:
            continue
        visited.add(oid)
        yield oid

        commit = get_commit(oid)
        oids.appendleft(commit.parent)


def get_oid(name):
    # If the "name" is a ref, we will get the oid corresponding
    # to that ref from `data.get_ref` function
    # Otherwise, if the name is not a ref, and an oid, we will
    # just return the oid (name)

    # "@" is an alias for "HEAD"
    if name == "@":
        name = "HEAD"

    # The refs can be in either of these directories or files:
    # Root (.ugit) -> refs/tags/{tagname}
    # .ugit/refs -> tags/{tagname}
    # .ugit/refs/{tags} -> {tagname}
    # .ugit/refs/heads

    refs_to_try = [
        f"{name}",
        f"refs/{name}",
        f"refs/tags/{name}",
        f"refs/heads/{name}",
    ]

    for ref in refs_to_try:
        if data.get_ref(ref, deref=False).value:
            return data.get_ref(ref).value

    # Check if the name is a sha1 hash or not
    # A SHA1 is a random 40-digit hexidecimal number
    is_hex = all(c in string.hexdigits for c in name)
    if len(name) == 40 and is_hex:
        return name

    raise ValueError(f"Unknown ref or oid: {name}")


def is_ignored(path):
    ignore_dirs = [".git", ".ugit", "ugit.egg-info", "__pycache__"]
    path_parts = pathlib.Path(path).parts
    for igd in ignore_dirs:
        if igd in path_parts:
            return True
    return False
