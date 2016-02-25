#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
from csv import DictWriter, DictReader

LOG_FILE = 'merge_results.log'
DEFAULT_OUTPUT_FILE = 'merged_search_results.csv'


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


if __name__ == "__main__":
    setup_logger()

    """Parse command line options
    """
    parser = argparse.ArgumentParser(description="Merge search results from"
                                     " multiple chunks")

    parser.add_argument('inputs', nargs='*', help='CSV input file(s) name')

    parser.add_argument("-o", "--out", type=str, dest="outfile",
                        default=DEFAULT_OUTPUT_FILE,
                        help="Output file in CSV (default: {0:s})"
                        .format(DEFAULT_OUTPUT_FILE))

    args = parser.parse_args()

    logging.info(str(args))

    out = open(args.outfile, 'wb')
    count = 0
    try:
        for n, i in enumerate(args.inputs):
            logging.info("Merging...: '{0}'".format(i))
            with open(i, 'rb') as f:
                reader = DictReader(f)
                if n == 0:
                    writer = DictWriter(out, fieldnames=reader.fieldnames)
                    writer.writeheader()
                for r in reader:
                    writer.writerow(r)
                    count += 1
    except Exception as e:
        logging.error(e)
    finally:
        out.close()

    logging.info("Done! (merge: {0} rows, from {1} files"
                 .format(count, len(args.inputs)))
