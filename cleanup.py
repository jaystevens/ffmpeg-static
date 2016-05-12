#!/usr/bin/env python

import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cleanup build folders: compile output target output.tar.xz')
    parser.add_argument('-a', '--all', dest='all',
            help='cleanup all (including "sourcegit" and "sourcetar")', action='store_true',
            default=False)
    args = parser.parse_args()

    deleteList = ['compile', 'output', 'target', 'output.tar.xz']
    if args.all is True:
        deleteList.append('sourcetar')
        deleteList.append('sourcegit')
    for item in deleteList:
        os.system('rm -rf ./%s' % item)


