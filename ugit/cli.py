import argparse
import os

from . import data

def main():
    args = parse_args()
    args.func(args)

def parse_args():
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(dest='command')
    commands.required = True

    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func=init)

    return parser.parse_args()


def init(args):
    dir_created = data.init()
    if dir_created:
        print(f"Initialized empty ugit repository in {os.getcwd()}\{data.GIT_DIR}")
    else:
        print(f"Ugit repo already exists at {os.getcwd()}")