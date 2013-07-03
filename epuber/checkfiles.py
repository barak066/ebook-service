#!/usr/bin/python
"""
Run this file about in 30 minutes
   ./checkfiles.py <directory with books>
"""

import sys, os, shutil, time

MAX_TIME = 60 * 30
MAX_SIZE = 50 * 1024 * 1024

def main(dir):
    names = os.listdir(dir)

    size = 0
    for name in names:
        size += os.stat(dir + name).st_size
        if  time.time() - os.stat(dir + name).st_atime > MAX_TIME:
            os.remove(dir + name)
    if size < MAX_SIZE:
        for name in names:
            os.remove(dir + name)

if __name__ == "__main__":
    main(sys.argv[1])
