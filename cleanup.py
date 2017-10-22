#!/usr/bin/env python

import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cleanup build folders: compile output target output.tar.xz')
    parser.add_argument('-g', '--gcc', dest='gcc', help='cleanup gcc', action='store_true', default=False)
    parser.add_argument('-a', '--all', dest='all',
            help='cleanup all (including "sourcegit" and "sourcetar")', action='store_true',
            default=False)
    args = parser.parse_args()

    deleteList = [
        os.path.join('sandbox', 'sys'),
        os.path.join('sandbox', 'build'),
        os.path.join('sandbox', 'result'),
    ]

    if args.all is True:
        deleteList.append('src')
        args.gcc = True
    if (args.gcc is True) or (args.all is True):
        deleteList.append(os.path.join('sandbox', 'sys_gcc'))

    for item in deleteList:
        print('removing ./%s' % item)
        os.system('rm -rf ./%s' % item)
    print('rmdir sandbox')
    os.system('rmdir sandbox')
    print('\nDONE')

