import argparse
import os
import sys
import textwrap
import subprocess

from . import data, base


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(dest="command")
    commands.required = True

    # Creating oid as type parsing function allows us to use
    # refs and oid interchangeably, as the oids corresponding
    # to the refs will be returned by this function
    oid = base.get_oid

    init_parser = commands.add_parser("init")
    init_parser.set_defaults(func=init)

    hash_object_parser = commands.add_parser("hash-object")
    hash_object_parser.add_argument("file")
    hash_object_parser.set_defaults(func=hash_object)

    cat_file_parser = commands.add_parser("cat-file")
    cat_file_parser.add_argument("object", type=oid)
    cat_file_parser.set_defaults(func=cat_file)

    write_tree_parser = commands.add_parser("write-tree")
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser("read-tree")
    read_tree_parser.add_argument("tree", type=oid)
    read_tree_parser.set_defaults(func=read_tree)

    commit_parser = commands.add_parser("commit")
    commit_parser.add_argument("-m", "--message", required=True)
    commit_parser.set_defaults(func=commit)

    log_parser = commands.add_parser("log")
    log_parser.add_argument("oid", nargs="?", type=oid, default="@")
    log_parser.set_defaults(func=log)

    checkout_parser = commands.add_parser("checkout")
    checkout_parser.add_argument("oid", type=oid)
    checkout_parser.set_defaults(func=checkout)

    tag_parser = commands.add_parser("tag")
    tag_parser.add_argument("name")
    tag_parser.add_argument("oid", nargs="?", type=oid, default="@")
    tag_parser.set_defaults(func=tag)

    k_parser = commands.add_parser("k")
    k_parser.set_defaults(func=k)

    branch_parser = commands.add_parser("branch")
    branch_parser.add_argument("name")
    branch_parser.add_argument("start_point", nargs="?", type=oid, default="@")
    branch_parser.set_defaults(func=branch)

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
    for oid in base.iter_commits_and_parents({args.oid}):
        commit = base.get_commit(oid)

        print(f"commit {oid}\n")
        print(textwrap.indent(commit.message, "\t"))
        print("")


def checkout(args):
    base.checkout(args.oid)


def tag(args):
    base.create_tag(args.name, args.oid)


def k(args):
    dot = "digraph commits {\n"
    oids = set()

    for refname, refoid in data.iter_refs():
        dot += f'"{refname}" [shape=note]\n'
        dot += f'"{refname}" -> "{refoid}"\n'
        oids.add(refoid)

    for oid in base.iter_commits_and_parents(oids):
        commit = base.get_commit(oid)
        dot += f'"{oid}" [shape=box style=filled label="{oid[:10]}"]\n'
        if commit.parent:
            dot += f'"{oid}" -> "{commit.parent}"\n'

    dot += "}"
    print(dot)

    with subprocess.Popen(
        ["dot", "-Tsvg", "-o", "ugitlog.svg"], stdin=subprocess.PIPE
    ) as proc:
        proc.communicate(dot.encode())


def branch(args):
    base.create_branch(args.name, args.start_point)
    print(f"Branch {args.name} created at {args.start_point[:10]}")
