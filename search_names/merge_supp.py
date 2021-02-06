#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import csv

DEFAULT_OUTPUT = "augmented_clean_names.csv"
DEFAULT_NAME_LOOKUP = "FirstName"
DEFAULT_PREFIX_LOOKUP = "seat"
PREFIX_FILE = "prefixes.csv"
NICK_NAMES_FILE = "nick_names.txt"

def parse_command_line(argv):
    """Parse command line options
    """
    parser = argparse.ArgumentParser(description="Merge supplement data")

    parser.add_argument('input', help='Input file name')

    parser.add_argument("-o", "--out", type=str, dest="outfile",
                        default=DEFAULT_OUTPUT,
                        help="Output file in CSV (default: {0!s})"
                        .format(DEFAULT_OUTPUT))
    parser.add_argument("-n", "--name", type=str, dest="name",
                        default=DEFAULT_NAME_LOOKUP,
                        help="Name of column use for nick name look up\
                        (default: {0!s})".format(DEFAULT_NAME_LOOKUP))
    parser.add_argument("-p", "--prefix", type=str, dest="prefix",
                        default=DEFAULT_PREFIX_LOOKUP,
                        help="Name of column use for prefix look up\
                        (default: {0!s})".format(DEFAULT_PREFIX_LOOKUP))
    parser.add_argument("--prefix-file", type=str, dest="prefix_file",
                        default=PREFIX_FILE,
                        help="CSV File contains list of prefixes\
                        (default: {0!s})".format(PREFIX_FILE))
    parser.add_argument("--nick-name-file", type=str, dest="nickname_file",
                        default=NICK_NAMES_FILE,
                        help="Text File contains list of nick names\
                        (default: {0!s})".format(NICK_NAMES_FILE))
    return parser.parse_args(argv)


def load_prefixes(filename, col):
    prefixes = {}
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for r in reader:
                prefixes[r[col]] = r['prefixes']
    except Exception as e:
        print('Prefix file {0!s} not found'.format(filename))

    return prefixes


def load_nick_names(filename):
    nick_names = {}
    try:
        with open(filename) as f:
            for l in f:
                l = l.strip().lower()
                if len(l): # null string
                    continue
                a = l.split('-')
                if len(a) >= 2:
                    names = a[0].split(',')
                    names = [s.strip() for s in names]
                    nicks = a[1].split(',')
                    nicks = [s.strip() for s in nicks]
                    nicks = ';'.join(nicks)
                    for n in names:
                        if n in nick_names:
                            print("WARNING: duplicate nick name '{0!s}' for "
                                "'{1!s}'".format(nicks, n))
                        else:
                            nick_names[n] = nicks
                else:
                    print("WARNING: Invalid nick name line '{0!s}'".format(l))
    except Exception as e:
        print('Nick name file {0!s} not found'.format(filename))

    return nick_names


def merge_supp(infile=None, prefixarg=DEFAULT_PREFIX_LOOKUP, name=DEFAULT_NAME_LOOKUP, outfile=DEFAULT_OUTPUT,
               prefix_file=PREFIX_FILE, nickname_file=NICK_NAMES_FILE):
    """Merge supplement data to names file
    """
    
    prefixes = load_prefixes(prefix_file, prefixarg)
    nick_names = load_nick_names(nickname_file)

    try:
        f = None
        o = None
        f = open(infile, 'r')
        reader = csv.DictReader(f)
        o = open(outfile, 'w')
        writer = csv.DictWriter(o, fieldnames=reader.fieldnames +
                                ['prefixes', 'nick_names'])
        writer.writeheader()

        for i, r in enumerate(reader):
            print("#{0}: {1!s}".format(i, r[name].lower()))
            # Prefix
            k = r[prefixarg]
            if k in prefixes:
                prefix = prefixes[k]
            else:
                prefix = ''
            r['prefixes'] = prefix
            # Nick name
            k = r[name].lower()
            if k in nick_names:
                nick = nick_names[k]
            else:
                nick = ''
            r['nick_names'] = nick
            writer.writerow(r)
    except Exception as e:
        raise
        print(e)
    finally:
        if o:
            o.close()
        if f:
            f.close()

    print("Done.")


def main(argv=sys.argv[1:]):

    args = parse_command_line(argv)

    print(args)

    print("Merging to '{0!s}', please wait...".format(args.outfile))

    merge_supp(args.input, args.prefix, args.name, args.outfile, args.prefix_file, args.nickname_file)

    return 0


if __name__ == "__main__":

    sys.exit(main())
