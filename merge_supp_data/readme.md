## Merge Supplementary Data

The script takes output from [clean-names](../clean-names) (see [sample input file](sample_in.csv)) and appends supplementary data (prefixes, nicknames) to the file (see [sample output file](augmented_clean_names.csv)). In particular, the script merges two supplementary data files:

1. **Prefixes:**  
  Generally the same set of prefixes will be used for a group of names. For instance, if you have a long list of politicians, state governors with no previous legislative experience will only have prefixes Governor, Mr., Mrs., Ms. etc., and not prefixes like Congressman or Congresswoman. We require a column in the input file that captures information about which 'prefix group' a particular name belongs to. We use that column to merge prefix data. The prefix file itself needs two columns: 1) A column to look up prefixes for groups of names depending on the value. The name of the column must be the same as the column name specified by the argument `-p/--prefix` (default is `seat`), and 2) a column of prefixes (multiple prefixes separated by semi-colon). The default name of the prefix data file is `prefixes.csv`. See [sample prefixes data file](prefixes.csv).   

2. **Nicknames:**  
  Nicknames are merged using first names in the input data file. The nicknames file is a plain text file. Each line contains single or list of first names on left side of the '-' and one or multiple nicknames on the right hand side. List of first names and nicknames must be separated by comma. Default name of the nicknames data file is `nick_names.txt`. See [sample nicknames file](nick_names.txt).  

### Usage

```
usage: merge_supp.py [-h] [-o OUTFILE] [-p PREFIX] [-n NAME] input

Merge supplementary data

positional arguments:
  input                 Input file name

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --out OUTFILE
                        Output file in CSV (default:
                        augmented_clean_names.csv)
  -p PREFIX, --prefix PREFIX
                        Name of column use for prefix look up (default: seat)
  -n NAME, --name NAME  Name of column use for nick name look up (default:
                        FirstName)
```

### Example

```
python merge_supp.py sample_in.csv
```

The script takes [sample_in.csv](sample_in.csv), [prefixes.csv](prefixes.csv), and [nick_names.txt](nick_names.txt) and produces [augmented_clean_names.csv](augmented_clean_names.csv). The output file has two additional columns:

* `prefixes` - List of prefixes (separated by semi-colon)  
* `nick_names` - List of nick names (separated by semi-colon)
