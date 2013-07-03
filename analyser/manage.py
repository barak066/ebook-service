#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


import settings
import runners

if __name__ == '__main__':
    runners.setup_sys_path(settings)
    runners.setup_django_orm()
    argv = sys.argv[1:]
    command = runners.get_runner(argv)

    if command:
        module = __import__('runners.%s' % command, globals(),locals(),[command])
        module.main( argv[1:], dir=dir(module) )

