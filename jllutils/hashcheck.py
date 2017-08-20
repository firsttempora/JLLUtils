#!/usr/bin/env python
from __future__ import print_function

import argparse
from glob import glob
import hashlib
import os.path
import random
import sys

def shell_error(msg, exit_code=1):
    print(msg, file=sys.stderr)
    exit(exit_code)

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def choose_n_files(path, pattern, n):
    all_files = glob(os.path.join(path, pattern))
    if len(all_files) <= n:
        return all_files

    files = []
    for i in range(n):
        f = random.choice(all_files)
        all_files.remove(f)
        files.append(f)
    return files

def print_hashes(hash_file, pattern, n_files, *dirs):
    with open(hash_file, 'w') as fobj:
        for dir in dirs:
            files = choose_n_files(dir, pattern, n_files)
            for this_file in files:
                md5_hash = md5(this_file)
                fobj.write('{}: {}\n'.format(this_file, md5_hash))

def get_args():
    parser = argparse.ArgumentParser(description='Saves a list of MD5 hashes to a file')
    parser.add_argument('--files-per-dir', '-n', default=10, type=int,
                        help='Number of files per directory to hash, default %(default)s')
    parser.add_argument('--pattern', '-p', default='*',
                        help='Glob pattern to filter files chosen, default is %(default)s')
    parser.add_argument('out_file', help='File to save the list of hashes in')
    parser.add_argument('directories', nargs=argparse.REMAINDER, help='Directories to hash files from. At least one required.')

    args = parser.parse_args()

    if len(args.directories) < 1:
        shell_error('At least one directory must be specified')
    else:
        for this_dir in args.directories:
            if not os.path.isdir(this_dir):
                shell_error('{} is not a valid directory'.format(this_dir))

    return args.directories, args.out_file, args.pattern, args.files_per_dir

def main():
    directories, out_file, pattern, nfiles = get_args()
    print_hashes(out_file, pattern, nfiles, *directories)

if __name__ == '__main__':
    main()