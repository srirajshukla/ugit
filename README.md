# UGIT - a small git like vcs

## Commands 
1. ugit write-tree
    Writes the current state of the directories to object store
2. ugit read-tree [object hash]
    Retrieves the files from object id hash given

## Workflow
1. Imagine you work on some code and you want to save a version.
2. Run `ugit write-tree`
3. Store the object hash that was printed out somewhere
4. Continue working and repeat steps 2 and 3 as necessary.
5. If you want to return to a previous version, use `ugit read-tree [hash]`  to restore it to the working directory.
