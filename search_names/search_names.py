#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import ctypes
import argparse
import logging
import csv
import gzip
import six
from six.moves import range
try:
    csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
except:
    csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
import time
import signal

from six.moves.configparser import ConfigParser
from .searchengines import (SearchMultipleKeywords, NewSearchMultipleKeywords,
                           RESULT_FIELDS)

from multiprocessing import (Pool, TimeoutError)
from multiprocessing.managers import SyncManager
from queue import Empty

from . import utils


""" Defaults declaration
"""
MAX_NAME = 20
LOG_FILE = 'search_names.log'
DEF_OUTPUT_FILE = 'search_results.csv'
NUM_PROCESSES = 4

DEFAULT_TXT_COLNAME = 'text'
DEFAULT_INPUT_COLS = ['uniqid', 'text']
DEFAULT_SEARCH_OUTPUT_COLS = ['uniqid', 'n', 'match', 'start', 'end', 'count']
DEFAULT_EDITLENGTH = []
DEFAULT_NAME_FILE = 'deduped_augmented_clean_names.csv'
DEFAULT_COL_ID = 'uniqid'
DEFAULT_COL_SEARCH = 'search_name'


class WorkAroundManager(SyncManager):
    @staticmethod
    def _finalize_manager(process, address, authkey, state, _Client):
        try:
            SyncManager._finalize_manager(process, address, authkey, state,
                                          _Client)
        except WindowsError:
            # http://stackoverflow.com/questions/17076679/windowserror-access-is-denied-on-calling-process-terminate
            pass


def setup_logger(debug):
    """ Set up logging
    """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=LOG_FILE,
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter('%(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def parse_command_line(argv):
    """Parse command line arguments
    """
    parser = argparse.ArgumentParser(description="Search names in text corpus")

    parser.add_argument('input', help='CSV input file name')
    parser.add_argument("-m", "--max-name", type=int, dest="max_name",
                        default=MAX_NAME,
                        help="Maximum name in search results (default: {0:d})"
                        .format(MAX_NAME))
    parser.add_argument("-p", "--processes", type=int, dest="processes",
                        default=NUM_PROCESSES,
                        help="Number of processes to run (default: {0:d})"
                        .format(NUM_PROCESSES))
    parser.add_argument("-o", "--out", type=str, dest="outfile",
                        default=DEF_OUTPUT_FILE,
                        help="Search results in CSV (default: {0:s})"
                        .format(DEF_OUTPUT_FILE))
    parser.add_argument("-t", "--text", type=str, dest="text",
                        default=DEFAULT_TXT_COLNAME,
                        help="Column name with text (default: {0:s})"
                        .format(DEFAULT_TXT_COLNAME))
    parser.add_argument("-i", "--input-cols", type=int, nargs='+', dest="input_cols",
                        default=DEFAULT_INPUT_COLS,
                        help="List of column name from input file to include in the output\
                        (default: {0!s})".format(DEFAULT_INPUT_COLS))
    parser.add_argument("-c", "--search-cols", type=int, nargs='+', dest="search_cols",
                        default=DEFAULT_SEARCH_OUTPUT_COLS,
                        help="List of column name from search output\
                        (default: {0!s})".format(DEFAULT_SEARCH_OUTPUT_COLS))
    parser.add_argument('--overwritten', dest='overwritten',
                        action='store_true',
                        help='Overwritten if output file is exists')
    parser.add_argument("-e", "--editlength", type=int, nargs='+', dest="editlength",
                        default=DEFAULT_EDITLENGTH,
                        help="List of Edit Lengths\
                        (default: {0!s})".format(DEFAULT_EDITLENGTH))
    parser.add_argument('-f', '--file', dest='namefile',
                        default=DEFAULT_NAME_FILE,
                        help="CSV file contains unique ID and Name want to search for\
                        (default: {0!s})".format(DEFAULT_NAME_FILE))
    parser.add_argument('-u', '--uniqid', dest='name_id',
                        default=DEFAULT_COL_ID,
                        help="Column of unique ID in name want to search for\
                        (default: {0!s})".format(DEFAULT_COL_ID))
    parser.add_argument('-s', '--search', dest='name_search',
                        default=DEFAULT_COL_SEARCH,
                        help="Colunm of name want to search for\
                        (default: {0!s})".format(DEFAULT_COL_SEARCH))

    parser.set_defaults(overwritten=False)

    parser.add_argument('-d', '--debug', dest='debug',
                        action='store_true',
                        help="Enable debug message")

    parser.set_defaults(debug=False)

    parser.add_argument('--clean', dest='clean',
                        action='store_true',
                        help='Clean text column before search')

    parser.set_defaults(clean=False)

    return parser.parse_args(argv)


def load_names_file(namefile, col_id=DEFAULT_COL_ID, col_search=DEFAULT_COL_SEARCH):
    names = []
    logging.info("Load name file: {0}".format(namefile))
    with open(namefile, 'r') as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                names.append((r[col_id], r[col_search]))
            except:
                logging.error("Name file must have '{0}' and '{1}' columns"
                              .format(col_id, col_search))
    return names


def clean_text(s):
    s = utils.to_lower_case(s)
    s = utils.remove_special_chars(s)
    s = utils.remove_accents(s)
    s = utils.remove_stopwords(s)
    s = utils.remove_punctuation(s)
    s = utils.remove_extra_space(s)
    return s


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def worker(args):
    try:
        args, pid = args
        logging.info('[{0}] worker start'.format(pid))
        namesearch = NewSearchMultipleKeywords(args.names, args.editlength)
        _open = gzip.open if args.input.endswith('.gz') else open
        with _open(args.input, 'rt', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for i, r in enumerate(reader):
                if (i % args.processes) != pid:
                    continue
                text = r[args.text]
                if args.clean:
                    # clean text if need
                    text = clean_text(text)
                start = time.time()
                # Search and matching for nameslist
                result, n = namesearch.search(text, args.max_name)
                c = []
                for k in reader.fieldnames:
                    if k in args.input_cols:
                        if args.clean and k == args.text:
                            # replace original text with cleaned text
                            c.append(text)
                        else:
                            c.append(r[k])
                sel_result = []
                for i, r in enumerate(result):
                    k = RESULT_FIELDS[i % len(RESULT_FIELDS)]
                    if k in args.search_cols:
                        sel_result.append(r)
                c.extend(sel_result)
                if 'count' in args.search_cols:
                    c.append(n)
                elaspe = time.time() - start
                logging.debug("[{0}] found: {1} in {2:0.3f}s".format(pid, n, elaspe))
                args.result_queue.put(c)
                count += 1
        logging.info('[{0}] worker stop'.format(pid))
        return count
    except:
        import traceback
        traceback.print_exc()


def search_names(input, text=DEFAULT_TXT_COLNAME,
                 input_cols=DEFAULT_INPUT_COLS, names=[],
                 search_cols=DEFAULT_SEARCH_OUTPUT_COLS, max_name=MAX_NAME,
                 editlength=DEFAULT_EDITLENGTH, outfile=DEF_OUTPUT_FILE,
                 overwritten=False, processes=NUM_PROCESSES, clean=True):
    logging.info("Setting up, please wait...")

    args = argparse.Namespace()

    args.input = input
    args.text = text
    args.input_cols = input_cols
    args.names = names
    args.search_cols = search_cols
    args.max_name = max_name
    args.editlength = editlength
    args.outfile = outfile
    args.overwritten = overwritten
    args.processes = processes
    args.clean = clean

    if args.clean:
        utils.init_nltk()

    new_outfile = True
    """Create output file
    """
    try:
        if not os.path.exists(args.outfile) or args.overwritten:
            csvfile = open(args.outfile, 'w', encoding='utf-8')
        else:
            csvfile = open(args.outfile, 'a', encoding='utf-8')
            new_outfile = False
        csvwriter = csv.writer(csvfile, dialect='excel', delimiter=',',
                               quotechar='"', quoting=csv.QUOTE_MINIMAL)
    except:
        logging.error("Cannot create output file")
        return -1

    count = 0
    all_start = time.time()

    # Setting CSV header row
    if new_outfile:
        _open = gzip.open if args.input.endswith('.gz') else open
        with _open(args.input, 'rt') as f:
            reader = csv.DictReader(f)
            """Write output file headers
            """
            h = []
            for k in reader.fieldnames:
                if k in args.input_cols:
                    h.append(k)
            for i in range(args.max_name):
                for a in RESULT_FIELDS:
                    if a in args.search_cols:
                        h.append('name{0:d}.{1!s}'.format(i + 1, a))
            if 'count' in args.search_cols:
                h.append('count')
            csvwriter.writerow(h)

    # Setting up multiprocessing worker
    manager = WorkAroundManager()
    manager.start()
    # FIXME: Limit memory usage by set maxsize to twice a number of processes.
    args.result_queue = manager.Queue(args.processes * 2)
    pool = Pool(processes=args.processes, initializer=init_worker)
    result = pool.map_async(worker,
                            [(args, pid) for pid in range(args.processes)])

    # Getting the result from worker processes though share queue
    progress = 0
    while True:
        try:
            r = args.result_queue.get(timeout=0.1)
            csvwriter.writerow(r)
            progress += 1
            elaspe = time.time() - all_start
            logging.info("Progress: {0:d}, Average rate = {1:.0f} rows/min"
                          .format(progress, progress * 60 / elaspe))
        except KeyboardInterrupt:
            pool.terminate()
            pool.join()
            break
        except Empty:
            try:
                done = result.get(timeout=0.1)
                count = sum(done)
                break
            except TimeoutError:
                pass

    elaspe = time.time() - all_start
    logging.info("Total: {0:d}, Average rate = {1:.0f} rows/min"
                 .format(count, count * 60 / elaspe))
    csvfile.close()


def main(argv=sys.argv[1:]):

    args = parse_command_line(argv)

    setup_logger(args.debug)

    logging.info(str(args))

    names = load_names_file(args.namefile, args.name_id, args.name_search)

    search_names(args.input, args.text, args.input_cols, names,
                 args.search_cols, args.max_name, args.editlength,
                 args.outfile, args.overwritten, args.processes, args.clean)

    return 0

if __name__ == "__main__":
    sys.exit(main())
