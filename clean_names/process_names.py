#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

import names

DEFAULT_OUTPUT = "clean_names.csv"


def parse_command_line():
    """Parse command line options
    """
    parser = argparse.ArgumentParser(description="Clean name")

    parser.add_argument('input', help='Input file name')

    parser.add_argument("-o", "--out", action="store",
                        type=str, dest="outfile", default=DEFAULT_OUTPUT,
                        help="Output file in CSV (default: {0!s})"
                        .format(DEFAULT_OUTPUT))
    parser.add_argument("-c", "--column", action="store",
                        type=str, dest="column", default="Name",
                        help="Column name file in CSV contains Name list \
                        (default: Name)")
    parser.add_argument("-a", "--all", action="store_true",
                        dest="all", default=False,
                        help="Export all names (not take duplicate names out)\
                        (default: False)")
    return parser.parse_args()

if __name__ == "__main__":
    print("{0!s} - r4 (2016/01/02)\n".format(os.path.basename(sys.argv[0])))

    args = parse_command_line()

    print("Processing and exporting, please wait...")

    """Process and export names file
    """
    names.process_name_list(args.input, args.outfile, args.column,
                            args.all)

    print("Done.")
