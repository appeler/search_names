#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import splitext, basename, dirname
import ctypes
import argparse
import logging
import csv
from csv import DictWriter, DictReader
import sys

try:
    csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
except:
    csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

LOG_FILE = 'split_text_corpus.log'
DEFAULT_OUTPUT_FORMAT = 'chunk_{chunk_id:02d}/{basename}.csv'
DEFAULT_CHUNK_SIZE = 1000


def setup_logger():
    """ Set up logging
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=LOG_FILE,
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def split_text_corpus(infile=None, outfile=None, size=1000):
    with open(infile, 'r') as f:
        reader = DictReader(f)
        header = reader.fieldnames
        if 'uniqid' not in header:
            add_uid = True
            header.append('uniqid')
        else:
            add_uid = False
        chunk_id = 0
        count = 0
        uid = 0
        for r in reader:
            if count == 0:
                filename = splitext(basename(infile))[0]
                chunk_name = outfile.format(basename=filename,
                                                 chunk_id=chunk_id)
                logging.info("Create new chunk: {0}, filename: {1}"
                             .format(chunk_id, chunk_name))
                d = dirname(chunk_name)
                if not os.path.exists(d):
                    os.makedirs(d)
                out = open(chunk_name, 'w')
                writer = DictWriter(out, fieldnames=header)
                writer.writeheader()
            if add_uid:
                r['uniqid'] = uid
            writer.writerow(r)
            count += 1
            if count >= size:
                count = 0
                chunk_id += 1
                out.close()
            uid += 1


def main(argv=sys.argv[1:]):

    setup_logger()

    """Parse command line options
    """
    parser = argparse.ArgumentParser(description="Split large text corpus into"
                                     " smaller chunks")

    parser.add_argument('input', help='CSV input file name')

    parser.add_argument("-o", "--out", type=str, dest="outfile",
                        default=DEFAULT_OUTPUT_FORMAT,
                        help="Output file in CSV (default: {0:s})"
                        .format(DEFAULT_OUTPUT_FORMAT))
    parser.add_argument('-s', '--size', type=int, default=DEFAULT_CHUNK_SIZE,
                        help='Number of row in each chunk (default: {0:d})'
                        .format(DEFAULT_CHUNK_SIZE))

    args = parser.parse_args(argv)

    logging.info(str(args))

    split_text_corpus(args.input, args.outfile, args.size)
    logging.info("done.")

    return 0


if __name__ == "__main__":

    sys.exit(main())

