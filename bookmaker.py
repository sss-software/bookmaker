#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import shutil
import subprocess
import sys
import threading
import time
import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

__program__ = 'bookmaker'
__url__ = 'https://github.com/xorbyte/bookmaker/'
__author__ = 'alexandru'
__author_email__ = 'alex@hackd.net'
__copyright__ = 'Copyright (c) 2012'
__license__ = 'MIT'
__version__ = '0.2.1'
__description__ = 'Auto-convert epub/mobi ebooks in the monitored path(s).'

# Global Declarations
# ===================

# name of the conversion executable
EXEC_NAME = 'ebook-convert'
# known formats for conversion
OUT_FORMATS = set(['epub', 'mobi'])
IN_FORMATS = OUT_FORMATS.union(['lit'])
# number of workers to use for conversion
NUM_WORKERS = 2
# the work queue
worq = Queue.Queue()


class LibrarianDropBoxHandler(FileSystemEventHandler):
    """Handle modified-file events and kickstart conversion."""

    def __init__(self, formats, organize=True):
        super(LibrarianDropBoxHandler, self).__init__()
        self.formats = formats

    def on_modified(self, event):
        super(LibrarianDropBoxHandler, self).on_modified(event)
        if not event.is_directory:
            file_src = event.src_path
            # add a task for each of the formats still requiring conversion
            (parent, phile) = os.path.split(event.src_path)
            (name, sep_ext) = os.path.splitext(phile)
            ext = sep_ext.strip(os.path.extsep)

            # if we keep things organized, and the parent isn't named the same
            # as the current file, we'll create such a parent and move the
            # file in it
            if not os.path.split(parent)[1] == name:
                dest_dir = os.path.join(parent, name)
            else:
                dest_dir = parent
            if not os.path.exists(dest_dir):
                os.mkdir(dest_dir)
                shutil.move(file_src, dest_dir)
                file_src = os.path.join(dest_dir, phile)

            # either we don't keep organized (tsk) or we've already created
            # the containing folder, so we're triggering the conversion now
            if ext in IN_FORMATS:
                for fmt in OUT_FORMATS:
                    try_fmt = ''.join([name, os.path.extsep, fmt])
                    dest_path = os.path.join(dest_dir, try_fmt)
                    if not os.path.exists(dest_path):
                        worq.put((file_src, dest_path))


def parse_arguments(argv):
    # setup and parse arguments
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('monitor',
        action='store',
        metavar='PATH',
        nargs='*',
        help='path(s) to monitor')
    parser.add_argument('-p', '--paths',
        action='store',
        metavar='EXEC_PATH',
        nargs='*',
        default=[],
        help='additional path(s) to search for the conversion utility `%s` '
            '(see README for details)' % EXEC_NAME)
    parser.add_argument('-f', '--format',
        action='store',
        dest='formats',
        metavar='FMT',
        nargs='*',
        choices=OUT_FORMATS,
        default=OUT_FORMATS,
        help='format(s) to convert to (known: %s)' % ", ".join(OUT_FORMATS))
    parser.add_argument('-w', '--workers',
        action='store',
        type=int,
        default=NUM_WORKERS,
        help='number of conversion workers (default: %d)' % NUM_WORKERS)

    return parser.parse_args(args=argv)


def worker(exec_path):
    """Pick off a path from the queue and convert the book."""
    while True:
        (src, dest) = worq.get()
        subprocess.call([exec_path, src, dest])
        worq.task_done()


def main(argv):
    # create namespace with parsed arguments
    ns = parse_arguments(argv)
    # locate the executable (possibly causing an early termination)
    binpaths = os.environ.get('PATH').split(os.pathsep)
    # extend with user-supplied path, if appropriate
    if ns.paths:
        binpaths.extend(ns.paths)
    for binpath in binpaths:
        try_path = os.path.join(binpath, EXEC_NAME)
        if os.path.exists(try_path):
            exec_path = try_path
            break
    else:
        sys.stderr.write('Unable to locate the conversion utility `%s`\n'
            % EXEC_NAME)
        sys.stderr.write('$PATH:\n')
        for binpath in binpaths:
            sys.stderr.write('\t%s\n' % binpath)
        sys.stderr.write('Please see the README for more details.\n')
        sys.exit(1)

    # spin up some workers
    for i in range(ns.workers):
        t = threading.Thread(target=worker, args=(exec_path, ))
        t.daemon = True
        t.start()

    # create the filesystem observer and respective event handlers
    observer = Observer()
    for monitor_path in set(ns.monitor):
        if not os.path.exists(monitor_path):
            sys.stderr.write('Invalid path: %s\n' % monitor_path)
            sys.exit(2)
        else:
            event_handler = LibrarianDropBoxHandler(set(ns.formats))
            observer.schedule(event_handler, monitor_path, recursive=True)
    observer.start()

    # loop forever*
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.stdout.write('Waiting for tasks to finish and shutting down…')
        observer.stop()
    observer.join()
    worq.join()


if __name__ == '__main__':
    main(sys.argv[1:])
