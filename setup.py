#!/usr/bin/env python
import bookmaker
import os
import shutil
import sys
from distutils.core import setup


if not os.path.exists('./bin/'):
    os.mkdir('./bin/')
shutil.copyfile('bookmaker.py', './bin/bookmaker')


REQUIRES = ['watchdog']


setup(name=bookmaker.__program__,
        version=bookmaker.__version__,
        description=bookmaker.__description__,
        author=bookmaker.__author__,
        author_email=bookmaker.__author_email__,
        license=bookmaker.__license__,
        url=bookmaker.__url__,
        # packages=['bookmaker'],
        scripts=['./bin/bookmaker'])

sys.stdout.write('Cleaning up...\n')
[shutil.rmtree(dent, ignore_errors=True) for dent in ['./build/', './bin/']]
