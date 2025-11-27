#!/usr/bin/env python

import argparse
import csv
import os
import re
import sys

from nameparser import HumanName

from .logging_config import get_logger

logger = get_logger("clean_names")

DEFAULT_OUTPUT = "clean_names.csv"
re_std_suffix = re.compile(r"(JR|SR|PHD)[^\.]", flags=re.I)

def parse_command_line(argv):
    """Parse command line options
    """
    parser = argparse.ArgumentParser(description="Clean name")

    parser.add_argument('input', help='Input file name')

    parser.add_argument("-o", "--out", action="store",
                        type=str, dest="outfile", default=DEFAULT_OUTPUT,
                        help=f"Output file in CSV (default: {DEFAULT_OUTPUT!s})"
                        )
    parser.add_argument("-c", "--column", action="store",
                        type=str, dest="column", default="Name",
                        help="Column name file in CSV contains Name list \
                        (default: Name)")
    parser.add_argument("-a", "--all", action="store_true",
                        dest="all", default=False,
                        help="Export all names (not take duplicate names out)\
                        (default: False)")
    return parser.parse_args(argv)


def clean_names(infile, outfile=DEFAULT_OUTPUT, col="Name", all=False):
    """ Read names and pre-process
        Returns unique names in format "FirstName LastName AnyRomanNumeral"\
        or "FirstName LastName"
    """
    logger.info("Processing and exporting, please wait...")

    ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    if outfile:
        try:
            of = open(outfile, 'w')
        except OSError:
            outfile = None

    with open(infile) as f:
        reader = csv.DictReader(f)
        if outfile:
            writer = csv.DictWriter(of, fieldnames=reader.fieldnames +
                                    ['uniqid', 'FirstName',
                                     'MiddleInitial/Name', 'LastName',
                                     'RomanNumeral', 'Title', 'Suffix'])
            writer.writeheader()
        rowid = 0
        allnames = []
        allnameswithid = []
        for r in reader:
            rname = r[col]
            for name in re.split('[&/]', rname):
                name, n = re.subn(r'\s*\(.*\)\s*', ' ', name)
                if n > 0:
                    #print "Remove Parenthesis...", name
                    pass
                name, n = re.subn(r'\s*[\'"].*[\"\']\s*', ' ', name)
                if n > 0:
                    #print "Remove Quote...", name
                    pass
                name = HumanName(name)
                if name.last == '':
                    a = name.suffix.split(',')
                    if len(a) >= 2:
                        name = HumanName(name.first + ', ' + a[1] + ' ' + a[0])
                first = name.first.lower()
                mid = name.middle.lower()
                roman = ""
                title = name.title

                last = ""
                suffix_list = []
                for s in name.suffix.split(','):
                    if s.strip() in ROMAN:
                        roman = s
                        last = name.last.lower() + ' ' + roman.strip().lower()
                    else:
                        suffix_list.append(s)
                if last == "":
                    last = name.last.lower()
                suffix = ', '.join(suffix_list)

                if last == '':
                    logger.debug(f"Empty last name for: {repr(name)}")

                # Fixed ROMAN and Title in Middle
                if mid != "":
                    m_list = mid.split()
                    m = m_list[-1].strip()
                    m = m.strip('.')
                    if len(m_list) > 1 and m.upper() in ROMAN:
                        roman = m
                        mid = ' '.join(m_list[:-1])
                        #print rname, "==>", roman, "==>", mid
                    if m in ['mr', 'ms']:
                        title = m
                        mid = ' '.join(m_list[:-1])
                        #print rname, "==>", title, "==>", mid

                # Adhoc fixed for Title
                if title in ['POPE', "BARON", "MAHDI"]:
                    first = title + ' ' + first
                    #print rname, "==>", title, "==>", first
                    title = ""

                # Standardize Jr/Sr suffix
                suffix = re_std_suffix.sub(r'\1.', suffix + ' ').strip()

                # Standardize Middle Initial
                std_mid = []
                for m in mid.split():
                    if len(m) == 1:
                        m = m + '.'
                    std_mid.append(m)
                mid = ' '.join(std_mid)

                if all or (first, mid, last) not in allnames:
                    rowid += 1
                    r['uniqid'] = rowid
                    allnameswithid.append((r['uniqid'], first, mid, last,
                                           r['seat'].strip()))
                    allnames.append((first, mid, last))
                    #print "Add...", r['uniqid'], first, "-", mid, "-", last, "-", r['seat'].strip()
                    s = {'FirstName': first.upper(),
                         'MiddleInitial/Name': mid.upper(),
                         'LastName': name.last,
                         'RomanNumeral': roman.upper(),
                         'Title': title.upper(),
                         'Suffix': suffix.upper()}
                    t = dict(r, **s)
                    if outfile:
                        writer.writerow(t)
        if outfile:
            of.close()
        logger.info("Done.")
        return allnameswithid
    return None


def main(argv=sys.argv[1:]):

    args = parse_command_line(argv)
    logger.debug(f"Arguments: {args}")

    clean_names(args.input, args.outfile, args.column, args.all)

    return 0


if __name__ == '__main__':
    from .logging_config import setup_logging
    setup_logging()
    logger.info(f"Starting {os.path.basename(sys.argv[0])}")
    sys.exit(main())
