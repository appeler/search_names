#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
import csv
try:
    csv.field_size_limit(sys.maxsize)
except:
    csv.field_size_limit(sys.maxint)
import time
import signal

from ConfigParser import ConfigParser
from searchengines import (SearchMultipleKeywords, NewSearchMultipleKeywords,
                           RESULT_FIELDS)

from multiprocessing import (Pool, TimeoutError)
from multiprocessing.managers import SyncManager
from Queue import Empty

import preprocess


__version__ = "0.0.1"

""" Defaults declaration
"""
MAX_NAME = 20
LOG_FILE = 'search_names.log'
DEF_OUTPUT_FILE = 'search_results.csv'
DEFAULT_CONFIG_FILE = "search_names.cfg"
NUM_PROCESSES = 4


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


def parse_command_line():
    """Parse command line arguments
    """
    parser = argparse.ArgumentParser(description="Search names in text corpus")

    parser.add_argument('input', help='CSV input file name')
    parser.add_argument("-c", "--config", type=str, dest="config",
                        default=DEFAULT_CONFIG_FILE,
                        help="Default configuration file\
                        (default: {0!s})".format(DEFAULT_CONFIG_FILE))
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

    parser.add_argument('--overwritten', dest='overwritten',
                        action='store_true',
                        help='Overwritten if output file is exists')
    parser.set_defaults(overwritten=False)

    parser.add_argument('-d', '--debug', dest='debug',
                        action='store_true',
                        help="Enable debug message")
    parser.set_defaults(debug=False)

    parser.add_argument('--clean', dest='clean',
                        action='store_true',
                        help='Clean text column before search')
    parser.set_defaults(clean=False)

    return parser.parse_args()


def load_config(args=None):
    if args is None or isinstance(args, basestring):
        namespace = argparse.Namespace()
        if args is None:
            namespace.config = DEFAULT_CONFIG_FILE
        else:
            namespace.config = args
        args = namespace
    try:
        config = ConfigParser()
        config.read(args.config)
        args.namefile = config.get('name', 'file')
        args.name_id = config.get('name', 'id')
        args.name_search = config.get('name', 'search')
        args.editlength = []
        i = 1
        while True:
            k = 'edit' + str(i)
            try:
                l = config.getint('editlength', k)
                args.editlength.append((l, i))
                i += 1
            except:
                break
        # column name for text
        args.text = config.get('input', 'text')

        args.search_cols = []
        with open('search_cols.txt') as f:
            for l in f:
                if not l.startswith('#') and l.strip() != '':
                        args.search_cols.append(l.strip())
        args.input_file_cols = []
        with open('input_file_cols.txt') as f:
            for l in f:
                if not l.startswith('#') and l.strip() != '':
                    args.input_file_cols.append(l.strip())

    except Exception as e:
        print(e)

    return args


def load_names_file(args):
    args.names = []
    logging.info("Load name file: {0}".format(args.namefile))
    with open(args.namefile, 'rb') as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                args.names.append((r[args.name_id], r[args.name_search]))
            except:
                logging.error("Name file must have '{0}' and '{1}' columns"
                              .format(args.name_id, args.name_search))
                sys.exit(-2)
    return args.names


def clean_text(s):
    s = preprocess.to_lower_case(s)
    s = preprocess.remove_special_chars(s)
    s = preprocess.remove_accents(s)
    s = preprocess.remove_stopwords(s)
    s = preprocess.remove_punctuation(s)
    s = preprocess.remove_extra_space(s)
    return s


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def worker(args):
    try:
        args, pid = args
        logging.info('[{0}] worker start'.format(pid))
        namesearch = NewSearchMultipleKeywords(args.names, args.editlength)
        with open(args.input, 'rb') as f:
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
                    if k in args.input_file_cols:
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

if __name__ == "__main__":

    args = parse_command_line()

    setup_logger(args.debug)

    args = load_config(args)
    logging.info(str(args))

    logging.info("Setting up, please wait...")
    load_names_file(args)

    if args.clean:
        preprocess.init_nltk()

    new_outfile = True
    """Create output file
    """
    try:
        if not os.path.exists(args.outfile) or args.overwritten:
            csvfile = open(args.outfile, 'wb')
        else:
            csvfile = open(args.outfile, 'ab')
            new_outfile = False
        csvwriter = csv.writer(csvfile, dialect='excel', delimiter=',',
                               quotechar='"', quoting=csv.QUOTE_MINIMAL)
    except:
        logging.error("Cannot create output file")
        sys.exit(-1)

    count = 0
    all_start = time.time()

    # Setting CSV header row
    if new_outfile:
        with open(args.input, 'rb') as f:
            reader = csv.DictReader(f)
            """Write output file headers
            """
            h = []
            for k in reader.fieldnames:
                if k in args.input_file_cols:
                    h.append(k)
            for i in range(args.max_name):
                for a in RESULT_FIELDS:
                    if a in args.search_cols:
                        h.append('name%d.%s' % (i + 1, a))
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
