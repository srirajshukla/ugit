# UGIT - a small git like vcs

## Installation
### Dev Version
```
python setup.py develop --user
pip install -e .
```

## Commands 
1. ugit commit -m "commit message"
    Creates a commit with the given message
2. ugit log [ref/oid]
    Shows the log from given ref or oid. Defaults to HEAD
3. ugit checkout ref/oid
    Restore the worktree from given ref/oid
4. ugit tag name [ref/oid]
    Tag a given ref/oid. Defaults to HEAD

### Internal Commands
1. ugit write-tree
    Writes the current state of the directories to object store
2. ugit read-tree [object hash]
    Retrieves the files from object id hash given


## Features
- [x] Commit
- [x] Logs
- [x] Checkout
- [x] Tags

## Workflow
1. Imagine you work on some code and you want to save a version.
2. Run `ugit commit -m "commit message"`
3. You can tag the commit with `ugit tag mainidea`
4. Continue working and repeat steps 2 and 3 as necessary.
5. If you want to return to a previous version, use `ugit checkout ref/oid`  to restore it to the working directory. This essentialy creates a new "branch" where you can work separetly.
6. You can commit the changes on this branch as well, and tag them. 
7. Return to whichever tags you want to work with. 
