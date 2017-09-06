from __future__ import print_function

import subprocess
import os
import pdb

def filter_unlisted(list_file, extensions, log_file='gitfilter.log', git_dir='.', dryrun=False):
    if not os.path.isdir(git_dir):
        raise ValueError('git_dir does not exist')

    with open(list_file, 'r') as f:
        keep_files = [_make_relative_to_git_dir(s.strip(), git_dir) for s in f.readlines()]

    with open(log_file, 'w') as log:
        for root, dir_names, file_names in os.walk(git_dir):
            if '.git' in dir_names:
                dir_names.remove('.git')
            for f in file_names:
                if os.path.basename(f).startswith('.git'):
                    continue

                f = _make_relative_to_git_dir(os.path.join(root, f), git_dir)

                _, file_ext = os.path.splitext(f)

                if f not in keep_files and file_ext in extensions:
                    cmd = 'git-filter-file ' + f
                    if dryrun:
                        print('command: {}'.format(cmd))
                    else:
                        subprocess.check_call(cmd, cwd=git_dir, shell=True)
                        log.write(cmd + '\n')


def _make_relative_to_git_dir(path, git_dir):
    dir_contents = os.listdir(git_dir)
    path_pieces = path.split(os.path.sep)
    for piece in path_pieces:
        if piece in dir_contents:
            i = path_pieces.index(piece)
            return os.path.join(*path_pieces[i:])