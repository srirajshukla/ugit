import argparse
import os
import sys
import textwrap

from . import data, base


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(dest="command")
    commands.required = True

    init_parser = commands.add_parser("init")
    init_parser.set_defaults(func=init)

    hash_object_parser = commands.add_parser("hash-object")
    hash_object_parser.add_argument("file")
    hash_object_parser.set_defaults(func=hash_object)

    cat_file_parser = commands.add_parser("cat-file")
    cat_file_parser.add_argument("object")
    cat_file_parser.set_defaults(func=cat_file)

    write_tree_parser = commands.add_parser("write-tree")
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser("read-tree")
    read_tree_parser.add_argument("tree")
    read_tree_parser.set_defaults(func=read_tree)

    commit_parser = commands.add_parser("commit")
    commit_parser.add_argument("-m", "--message", required=True)
    commit_parser.set_defaults(func=commit)

    log_parser = commands.add_parser("log")
    log_parser.add_argument("oid", nargs="?")
    log_parser.set_defaults(func=log)

    checkout_parser = commands.add_parser("checkout")
    checkout_parser.add_argument("oid")
    checkout_parser.set_defaults(func=checkout)

    tag_parser = commands.add_parser("tag")
    tag_parser.add_argument("name")
    tag_parser.add_argument("oid", nargs="?")
    tag_parser.set_defaults(func=tag)

    return parser.parse_args()


def init(args):
    dir_created = data.init()
    if dir_created:
        print(f"Initialized empty ugit repository in {os.getcwd()}\{data.GIT_DIR}")
    else:
        print(f"Ugit repo already exists at {os.getcwd()}")


def hash_object(args):
    with open(args.file, "rb") as f:
        print(data.hash_object(f.read()))


def cat_file(args):
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(args.object, expected_type=None))


def write_tree(args):
    print(base.write_tree())


def read_tree(args):
    base.read_tree(args.tree)


def commit(args):
    print(base.commit(args.message))


def log(args):
    oid = args.oid or data.get_ref("HEAD")

    while oid:
        commit = base.get_commit(oid)

        print(f"commit {oid}\n")
        print(textwrap.indent(commit.message, "\t"))
        print("")

        oid = commit.parent


def checkout(args):
    base.checkout(args.oid)


def tag(args):
    oid = args.oid or data.get_ref("HEAD")
    base.create_tag(args.name, oid)
