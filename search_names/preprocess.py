#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import csv
import itertools

from copy import copy
import traceback

from Levenshtein import distance
from .logging_config import get_logger

logger = get_logger("preprocess")

DEFAULT_OUTPUT = "deduped_augmented_clean_names.csv"
DEFAULT_DROP_PATTERNS = "drop_patterns.txt"
DEFAULT_PATTERNS = ["FirstName LastName", "NickName LastName", "Prefix LastName"]
DEFAULT_EDITLENGTH = []

def parse_command_line(argv):
    """Parse command line options
    """
    parser = argparse.ArgumentParser(description="Preprocess Search List")

    parser.add_argument('input', help='Input file name')

    parser.add_argument("-o", "--out", type=str, dest="outfile",
                        default=DEFAULT_OUTPUT,
                        help="Output file in CSV (default: {0!s})"
                        .format(DEFAULT_OUTPUT))
    parser.add_argument("-d", "--drop-patterns", type=str, dest="drop_patterns_file",
                        default=DEFAULT_DROP_PATTERNS,
                        help="File with Default Patterns\
                        (default: {0!s})".format(DEFAULT_DROP_PATTERNS))
    parser.add_argument("-p", "--patterns", type=str, nargs='+', dest="patterns",
                        default=DEFAULT_PATTERNS,
                        help="List of Default Patterns\
                        (default: {0!s})".format(DEFAULT_PATTERNS))
    parser.add_argument("-e", "--editlength", type=int, nargs='+', dest="editlength",
                        default=DEFAULT_EDITLENGTH,
                        help="List of Edit Lengths\
                        (default: {0!s})".format(DEFAULT_EDITLENGTH))
    return parser.parse_args(argv)


def load_drop_patterns(filename):
    drop_patterns = []
    try:
        with open(filename) as f:
            for l in f:
                l = l.strip().lower()
                if len(l): # null string
                    continue
                drop_patterns.append(l)
    except Exception as e:
        logger.warning(f'Drop pattern file {filename} not found')
    return drop_patterns


def preprocess(infile = None, patterns = DEFAULT_PATTERNS, outfile = DEFAULT_OUTPUT, editlength = DEFAULT_EDITLENGTH, drop_patterns = None):
    """Preprocessing names file
    """
    logger.info(f"Preprocessing to '{outfile}', please wait...")
    o = None

    try:
        f = None
        f = open(infile, 'r')
        reader = csv.DictReader(f)
        out = []
        logger.info("Building search names...")
        for i, r in enumerate(reader):
            logger.debug(f"#{i}:")
            for p in patterns:
                logger.debug(f"Pattern: '{p}'")
                parr = p.split()
                s = []
                for a in parr:
                    a = a.strip()
                    if a == 'Prefix':
                        prefixes = r['prefixes'].split(';')
                        s.append(prefixes)
                    elif a == 'NickName':
                        nick_names = r['nick_names'].split(';')
                        s.append(nick_names)
                    else:
                        s.append([r[a].lower()])
                combines = list(itertools.product(*s))
                for c in combines:
                    c = [d for d in c if len(d)]
                    if len(c) > 1:
                        name = ' '.join(c)
                        if name not in drop_patterns:
                            logger.debug(f" Name: '{name}'")
                            new_r = copy(r)
                            new_r['search_name'] = name
                            out.append(new_r)

        # Find duplicate indexes
        logger.info("Finding duplicates...")
        dup = set()
        for i, r in enumerate(out):
            name1 = r['search_name']
            # Get max edit distance
            max_dist = 0
            for k, l in enumerate(editlength):
                if len(name1) > l:
                    max_dist = k + 1
            uid1 = r['uniqid']
            if i not in dup:
                for j in range(i + 1, len(out)):
                    name2 = out[j]['search_name']
                    uid2 = out[j]['uniqid']
                    if distance(name1, name2) <= max_dist:
                        if (uid1 != uid2):
                            # Drop both if from difference uid
                            dup.add(i)
                            dup.add(j)
                        else:
                            # Drop only one if from same uid
                            dup.add(j)

        # Remove duplicates (reversed order)
        logger.info("Removing duplicates...")
        dup = sorted(list(dup), reverse=True)
        for i in dup:
            del out[i]

        # Write out to output file
        logger.info(f"Writing output to file: '{outfile}'")
        o = open(outfile, 'w')
        writer = csv.DictWriter(o, fieldnames=reader.fieldnames +
                                ['search_name'])
        writer.writeheader()
        for r in out:
            writer.writerow(r)
    except Exception as e:
        traceback.print_exc()

    finally:
        if o:
            o.close()
        if f:
            f.close()
    logger.info("Done.")


def main(argv=sys.argv[1:]):

    args = parse_command_line(argv)

    args.drop_patterns = load_drop_patterns(args.drop_patterns_file)

    logger.debug(f"Arguments: {args}")
  
    preprocess(args.input, args.patterns, args.outfile, args.editlength, args.drop_patterns)

    return 0


if __name__ == "__main__":

    sys.exit(main())

