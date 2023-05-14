import argparse
import os
import sys

from . import data


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
