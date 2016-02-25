## Preprocess Search List

The script takes the output from [merge supp. data](../merge_supp_data/) ([sample input file](augmented_clean_names.csv)), list of patterns we want to search for, an ad hoc list of patterns we want to drop ([sample drop patterns file](drop_patterns.txt), and relative edit distance (based on the length of the pattern we are searching for) for approximate matching and does three things: a) creates a row for each pattern we want to search for (duplicating all the supplementary information), b) drops the ad hoc list of patterns we want to drop and c) de-duplicates based on edit distance and patterns we want to search for. See [sample output file](deduped_augmented_clean_names.csv).

The script relies on a configuration file, [`preprocess.cfg`](preprocess.cfg), that allows users to describe the patterns to search for, name of the file containing patterns we want to drop, and edit distance.

### Installation

Begin by installing the dependencies: 

```
pip install -r requirements.txt
```

### Configuration file

There are three sections in the [configuration file](preprocess.cfg): 

1) search

This section contains patterns ---combination of field names---we want to search for:

```
    [search]
    pattern1 = FirstName LastName
    pattern2 = NickName LastName
    pattern3 = Prefix LastName
```

2) drop

 The `file` variable points to the file containing list of people to be dropped. Usually, this file is an ad hoc list of patterns that we want removed. For instance, patterns matching famous people not on the list.

```
    [drop]
    file = drop_patterns.txt
```

3) editlength

This section contains minimum name length for the specific string length. For instance, `edit1=10` means that for patterns of length 10 or more, match within edit distance of 1.

```
    [editlength]
    edit1 = 10
    edit2 = 20
```

If you want to disable `fuzzy' matching, just comment out edit1 and edit2 using a hash sign as follows:

```
# edit1 = 10
# edit2 = 20
```

### Usage

```
usage: preprocess.py [-h] [-o OUTFILE] [-c CONFIG] input

Preprocess Search List

positional arguments:
  input                 Input file name

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --out OUTFILE
                        Output file in CSV (default:
                        deduped_augmented_clean_names.csv)
  -c CONFIG, --config CONFIG
                        Default configuration file (default: preprocess.cfg)
```

### Example

```
python preprocess.py  augmented_clean_names.csv
```

By default, the output will be saved as `deduped_augmented_clean_names.csv`. The script adds a new column, `search_name` for unique search key.
