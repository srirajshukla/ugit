import os

GIT_DIR = ".ugit"


def init():
    try:
        os.makedirs(GIT_DIR)
        return True
    except OSError as e:
        return False
