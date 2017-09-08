#!/usr/bin/env python
from __future__ import print_function

import argparse
import subprocess
import os
import sys

import pdb


def shell_error(msg, exit_code=1):
    print(msg, file=sys.stderr)
    exit(exit_code)


def filter_unlisted_in_file(list_file, extensions=None, log_file='gitfilter.log', git_dir='.', dry_run=False):
    with open(list_file, 'r') as f:
        keep_files = [s.strip() for s in f.readlines()]

    filter_unlisted(keep_files, extensions, log_file=log_file, git_dir=git_dir, dry_run=dry_run)


def filter_unlisted(keep_files, extensions=None, log_file='gitfilter.log', git_dir='.', dry_run=False):
    files_to_remove = []
    keep_files = [_make_relative_to_git_dir(f, git_dir) for f in keep_files]
    for root, dir_names, file_names in os.walk(git_dir):
        try:
            dir_names.remove('.git')
        except ValueError:
            pass

        for f in file_names:
            _, file_ext = os.path.splitext(f)

            f_path = os.path.join(root, f)

            if _make_relative_to_git_dir(f_path, git_dir) not in keep_files and (extensions is None or file_ext in extensions):
                files_to_remove.append(f_path)

    _run_filter_files(files_to_remove, log_file=log_file, git_dir=git_dir, dry_run=dry_run)


def filter_listed(file_list, log_file='gitfilter.log', git_dir='.', dry_run=False):
    _run_filter_files(file_list, log_file=log_file, git_dir=git_dir, dry_run=dry_run)


def filter_listed_in_file(list_file, log_file='gitfilter.log', git_dir='.', dry_run=False):
    with open(list_file, 'r') as f:
        remove_files = [s.strip() for s in f.readlines()]

    filter_listed(remove_files, log_file=log_file, git_dir=git_dir, dry_run=dry_run)


def _run_filter_files(files_to_remove, log_file='gitfilter.log', git_dir='.', dry_run=False):
    if not os.path.isdir(git_dir):
        raise ValueError('git_dir does not exist')

    files_to_remove_rel = [_make_relative_to_git_dir(f, git_dir) for f in files_to_remove if not os.path.basename(f).startswith('.git')]

    cmd = ['git', 'filter-branch', '--force', '--index-filter',
           '"git rm --cached --ignore-unmatch {}"'.format(" ".join(_escape_spaces(files_to_remove_rel))),
           '--prune-empty', '--tag-name-filter', 'cat', '--', '--all']
    cmd = ' '.join(cmd)

    if dry_run:
        print(cmd)
    else:
        with open(log_file, 'w') as log:
            # As far as I can tell, using shell=True is necessary because of the sub command for --index-filter
            # using the list of arguments syntax fails with a 'file too long' - it seems Python can't tell Git
            # very well what the separate arguments to git rm are
            subprocess.Popen(cmd, cwd=git_dir, stdout=log, stderr=log, shell=True).communicate()


def _make_relative_to_git_dir(path, git_dir):
    dir_contents = os.listdir(git_dir)
    path_pieces = path.split(os.path.sep)
    for piece in path_pieces:
        if piece in dir_contents:
            i = path_pieces.index(piece)
            return os.path.join(*path_pieces[i:])

    raise ValueError('Could not make {} relative to Git directory {}'.format(path, git_dir))


def _escape_spaces(list_str):
    return [s.replace(' ', '\ ') for s in list_str]


def _iter_git_branches(git_dir='.'):
    branches = subprocess.check_output(['git', 'for-each-ref', '--format=%(refname)', 'refs/heads']).splitlines()
    for b in branches:
        yield b


def _list_all_files_all_branches(git_dir='.'):
    # Credit to pratZ at https://stackoverflow.com/questions/27399006/git-list-all-files-in-a-directory-across-all-branches

    git_files = []
    for branch in _iter_git_branches(git_dir):
        git_files += subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', branch]).splitlines()

    return set(git_files)


def get_args():
    parser = argparse.ArgumentParser(description='Apply complex series of Git commands to a repository')
    parser.add_argument('action', default='filter', help='Which action to take. Possible values are: "filter" (remove files entirely from repo history)')
    parser.add_argument('-u', '--unlisted', action='store_true', help='Invert the filter to remove files not listed; thus this list becomes a list of files to keep')
    parser.add_argument('-e', '--extension', action='append', help='With --unlisted (-u), limits the file types that will be removed by extension. This argument can be given multiple times to specify multiple extensions.')
    parser.add_argument('-f', '--file', help='Read the list of files to remove (or keep with --unlisted) from the file specified rather than stdin')
    parser.add_argument('-d', '--git-dir', default='.', help='The directory containing the Git repository to act on. Default is current directory.')
    parser.add_argument('-X', '--dry-run', action='store_true', help='Do not execute the commands, instead print what will be run.')
    parser.add_argument('args', nargs='*', default=[], help='For action == "filter": The files to remove (or keep with --unlisted). If --file is given, these are ignored.')

    args = parser.parse_args()
    if args.action == 'filter':
        check_filter_args(args)
    else:
        shell_error('{} is not a valid action'.format(args.action))

    return args

def check_filter_args(args):
    if args.file is not None and not os.path.isfile(args.file):
        shell_error('Argument to --file (-f) is not a file')
    if not os.path.isdir(args.git_dir):
        shell_error('Argument to --git-dir (-d) is not a directory')
    if args.extension is not None:
        for ext in args.extension:
            if not ext.startswith('.'):
                shell_error('All extensions specified with --extension (-e) must start with a period')
    if args.file is None and len(args.args) == 0:
        shell_error('At least one file to remove/keep must be given if not reading a list of files from another file')



if __name__ == '__main__':
    args = get_args()

    if args.action == 'filter':
        if args.file is not None:
            if args.unlisted:
                filter_unlisted_in_file(args.file, args.extension, git_dir=args.git_dir, dry_run=args.dry_run)
            else:
                filter_listed_in_file(args.file, git_dir=args.git_dir, dry_run=args.dry_run)
        else:
            if args.unlisted:
                filter_unlisted(args.args, extensions=args.extension, git_dir=args.git_dir, dry_run=args.dry_run)
            else:
                filter_listed(args.args, git_dir=args.git_dir, dry_run=args.dry_run)