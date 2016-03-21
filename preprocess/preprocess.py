#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import csv
import itertools

from copy import copy
from ConfigParser import ConfigParser

from Levenshtein import distance

DEFAULT_OUTPUT = "deduped_augmented_clean_names.csv"
DEFAULT_CONFIG_FILE = "preprocess.cfg"


def parse_command_line():
    """Parse command line options
    """
    parser = argparse.ArgumentParser(description="Preprocess Search List")

    parser.add_argument('input', help='Input file name')

    parser.add_argument("-o", "--out", type=str, dest="outfile",
                        default=DEFAULT_OUTPUT,
                        help="Output file in CSV (default: {0!s})"
                        .format(DEFAULT_OUTPUT))
    parser.add_argument("-c", "--config", type=str, dest="config",
                        default=DEFAULT_CONFIG_FILE,
                        help="Default configuration file\
                        (default: {0!s})".format(DEFAULT_CONFIG_FILE))
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
        args.patterns = []
        i = 1
        while True:
            k = 'pattern' + str(i)
            try:
                p = config.get('search', k)
                args.patterns.append(p)
                i += 1
            except:
                break
        args.drop_patterns_file = config.get('drop', 'file')
        args.editlength = []
        i = 1
        while True:
            k = 'edit' + str(i)
            try:
                l = config.getint('editlength', k)
                args.editlength.append(l)
                i += 1
            except:
                break
    except Exception as e:
        print(e)

    print args

    return args


def load_drop_patterns(filename):
    drop_patterns = []
    with open(filename) as f:
        for l in f:
            l = l.strip().lower()
            if len(l): # null string
                continue
            drop_patterns.append(l)
    return drop_patterns


if __name__ == "__main__":

    args = parse_command_line()

    args = load_config(args)

    args.drop_patterns = load_drop_patterns(args.drop_patterns_file)

    print(args)

    print("Preprocessing to '{0!s}', please wait...".format(args.outfile))

    """Preprocessing names file
    """
    try:
        f = None
        f = open(args.input, 'rb')
        reader = csv.DictReader(f)
        out = []
        print("Build search names...")
        for i, r in enumerate(reader):
            print("#{0}:".format(i))
            for p in args.patterns:
                print("Pattern: '{0}'".format(p))
                parr = p.split()
                s = []
                for a in parr:
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
                        if name not in args.drop_patterns:
                            print(" Name: '{0}'".format(name))
                            new_r = copy(r)
                            new_r['search_name'] = name
                            out.append(new_r)

        # Find duplicate indexes
        print("Find duplicates...")
        dup = set()
        for i, r in enumerate(out):
            name1 = r['search_name']
            # Get max edit distance
            max_dist = 0
            for k, l in enumerate(args.editlength):
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
        print("De-duplicates...")
        dup = sorted(list(dup), reverse=True)
        for i in dup:
            del out[i]

        # Write out to output file
        print("Write the output to file: '{0}'".format(args.outfile))
        o = None
        o = open(args.outfile, 'wb')
        writer = csv.DictWriter(o, fieldnames=reader.fieldnames +
                                ['search_name'])
        writer.writeheader()
        for r in out:
            writer.writerow(r)

    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        if o:
            o.close()
        if f:
            f.close()

    print("Done.")
