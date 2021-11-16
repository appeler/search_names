Search Names: Search a long list of names in a large text corpus
-----------------------------------------------------------------

.. image:: https://github.com/appeler/search-names/workflows/test/badge.svg
    :target: https://github.com/appeler/search-names/actions?query=workflow%3Atest
.. image:: https://ci.appveyor.com/api/projects/status/lv4f7r8t2fat4kqp?svg=true
    :target: https://ci.appveyor.com/project/soodoku/search-names
.. image:: https://img.shields.io/pypi/v/search-names.svg
    :target: https://pypi.python.org/pypi/search-names
.. image:: https://readthedocs.org/projects/search-names/badge/?version=latest
    :target: http://search-names.readthedocs.io/en/latest/?badge=latest
.. image:: https://pepy.tech/badge/search-names
    :target: https://pepy.tech/project/search-names


There are seven kinds of challenges in searching a long list of names in a large text corpus:

1. Names may not be in a standard format, e.g., the first name may not always be followed by the last name, etc.

2. Searching FirstName LastName may not be enough. References to the person may take the form of Prefix LastName, etc. For instance, President Clinton.

3. Names may be misspelled.

4. Text may refer to people by their diminutive name (hypocorism), or by their middle name, or diminutive form of their middle name, etc. For instance, citations to Bill Clinton are liable to be much more common than William Clinton.

5. Names on the list may overlap with names not on the list, especially names of other famous people. For instance, searching for `Maryland politician <https://en.wikipedia.org/wiki/Michael_A._Jackson_(politician)>`__ Michael Jackson may yield lots of false positives.

6. Names on the list may match other names on the list (duplicates). 

7. Searching is computationally expensive. And searching for a long list over a large corpus is a double whammy.

We address each of the problems.

The Workflow
~~~~~~~~~~~~

Before anything else, use `clean_names`_ to standardize the names on the list. The script appends separate columns for prefix, first\_name, last\_name, etc. Some human curation will likely still be needed. Do it before going further. After that, use `merge supplementary data`_ to append other potential prefixes, diminutive norms of the first name, and other names by which the person is known by to the output of `clean_names`_. Next,
`preprocess`_ the search list. In particular, the script does three things:

1. **Converts the data from wide to long**: The script creates a
   separate row for each pattern we want to search for. For instance, if
   we add 'Bill' as a diminutive name for William, and in the
   configuration file, say, we want to only search for 'FirstName
   LastName', the script creates a separate row for 'William Clinton'
   and 'Bill Clinton', copying all other information across rows. And
   appends a column called 'search\_pattern.'

2. **Deduplicates**: it removes any 'pattern', say 'Prefix LastName'
   that is duplicated and hence cannot be easily disambiguated in
   search. (This can be turned off.) and

3. **Removes an ad hoc list of patterns**: For instance, patterns
   matching famous people not on the list, e.g. we can remove 'Michael
   Jackson' and it won't remove 'Congressman Jackson.'

Lastly, the `search`_ script searches patterns in the list in
a multi-threaded, parallelized way.

Installation
~~~~~~~~~~~~

We strongly recommend installing ``search-names`` inside a Python virtual environment (see `venv documentation <https://docs.python.org/3/library/venv.html#creating-virtual-environments>`__)

::

    pip install search_names


.. _`clean_names`: `Clean the name on the list`_

Clean the name on the list
~~~~~~~~~~~~~~~~~~~~~~~~~~

``clean_names``: The script is a modified version of `Clean Names <http://github.com/appeler/clean-names>`__.

The script takes a csv file with column 'Name' containing 'dirty names'--- names with all different formats: lastname firstname, firstname lastname, middlename lastname firstname etc. (see `sample input file <https://github.com/appeler/search_names/blob/master/examples/clean_names/sample_input.csv>`__\ ) and produces a csv file that has all the columns of the original csv file and the following columns: 'uniqid', 'FirstName', 'MiddleInitial/Name', 'LastName', 'RomanNumeral', 'Title', 'Suffix' (see `sample output file <https://github.com/appeler/search_names/blob/master/examples/clean_names/sample_output.csv>`__\ ).

Usage
^^^^^

::

   usage: clean_names [-h] [-o OUTFILE] [-c COLUMN] [-a] input

   Clean name

   positional arguments:
   input                 Input file name

   optional arguments:
   -h, --help            show this help message and exit
   -o OUTFILE, --out OUTFILE
                           Output file in CSV (default: clean_names.csv)
   -c COLUMN, --column COLUMN
                           Column name file in CSV contains Name list (default:
                           Name)
   -a, --all             Export all names (not take duplicate names out)
                           (default: False)

Example
^^^^^^^
::

    clean_names -a sample_input.csv


Merge Supplementary Data
~~~~~~~~~~~~~~~~~~~~~~~~

The script takes output from `clean_names`_ (see `sample input file <https://github.com/appeler/search_names/blob/master/examples/merge_supp_data/sample_in.csv>`__\ ) and appends supplementary data (prefixes, nicknames) to the file (see `sample output file <https://github.com/appeler/search_names/blob/master/examples/merge_supp_data/augmented_clean_names.csv>`__\ ). In particular, the script merges two supplementary data files:

   **Prefixes:** Generally the same set of prefixes will be used for a group of names. For instance, if you have a long list of politicians, state governors with no previous legislative experience will only have prefixes Governor, Mr., Mrs., Ms. etc., and not prefixes like Congressman or Congresswoman. We require a column in the input file that captures information about which 'prefix group' a particular name belongs to. We use that column to merge prefix data. The prefix file itself needs two columns: 1) A column to look up prefixes for groups of names depending on the value. The name of the column must be the same as the column name specified by the argument ``-p/--prefix`` (default is ``seat``\ ), and 2) a column of prefixes (multiple prefixes separated by semi-colon). The default name of the prefix data file is ``prefixes.csv``. See `sample prefixes data file <https://github.com/appeler/search_names/blob/master/examples/merge_supp_data/prefixes.csv>`__.

   **Nicknames:**  Nicknames are merged using first names in the input data file. The nicknames file is a plain text file. Each line contains single or list of first names on left side of the '-' and one or multiple nicknames on the right hand side. List of first names and nicknames must be separated by comma. Default name of the nicknames data file is ``nick_names.txt``. See `sample nicknames file <https://github.com/appeler/search_names/blob/master/examples/merge_supp_data/nick_names.txt>`__.

Usage
^^^^^

::

   usage: merge_supp [-h] [-o OUTFILE] [-n NAME] [-p PREFIX]
                     [--prefix-file PREFIX_FILE] [--nick-name-file NICKNAME_FILE]
                     input

   Merge supplement data

   positional arguments:
   input                 Input file name

   optional arguments:
   -h, --help            show this help message and exit
   -o OUTFILE, --out OUTFILE
                           Output file in CSV (default:
                           augmented_clean_names.csv)
   -n NAME, --name NAME  Name of column use for nick name look up (default:
                           FirstName)
   -p PREFIX, --prefix PREFIX
                           Name of column use for prefix look up (default: seat)
   --prefix-file PREFIX_FILE
                           CSV File contains list of prefixes (default:
                           prefixes.csv)
   --nick-name-file NICKNAME_FILE
                           Text File contains list of nick names (default:
                           nick_names.txt)

Example
^^^^^^^

::

   merge_supp sample_in.csv

The script takes `sample_in.csv <https://github.com/appeler/search_names/blob/master/examples/merge_supp_data/sample_in.csv>`__\ , `prefixes.csv <https://github.com/appeler/search_names/blob/master/examples/merge_supp_data/prefixes.csv>`__\ , and `nick_names.txt <https://github.com/appeler/search_names/blob/master/examples/merge_supp_data/nick_names.txt>`__ and produces `augmented_clean_names.csv <https://github.com/appeler/search_names/blob/master/examples/merge_supp_data/augmented_clean_names.csv>`__. The output file has two additional columns:


* ``prefixes`` - List of prefixes (separated by semi-colon)
* ``nick_names`` - List of nick names (separated by semi-colon)

.. _`preprocess`: `Preprocess Search List`_

Preprocess Search List
~~~~~~~~~~~~~~~~~~~~~~~

The script takes the output from `merge supp. data <https://github.com/appeler/search_names/blob/master/examples/merge_supp_data>`__ (\ `sample input file <https://github.com/appeler/search_names/blob/master/examples/preprocess/augmented_clean_names.csv>`__\ ), list of patterns we want to search for, an ad hoc list of patterns we want to drop (\ `sample drop patterns file <https://github.com/appeler/search_names/blob/master/examples/preprocess/drop_patterns.txt>`__\ , and relative edit distance (based on the length of the pattern we are searching for) for approximate matching and does three things: a) creates a row for each pattern we want to search for (duplicating all the supplementary information), b) drops the ad hoc list of patterns we want to drop and c) de-duplicates based on edit distance and patterns we want to search for. See `sample output file <https://github.com/appeler/search_names/blob/master/examples/preprocess/deduped_augmented_clean_names.csv>`__.

The script also takes arguments that define the patterns to search for, name of the file containing patterns we want to drop, and edit distance.

1) search

   An argument ``--patterns`` contains patterns---combination of field names---we want to search for. For instance ``--patterns "FirstName LastName" "NickName LastName" "Prefix LastName"`` means that we want to search for combination of "FirstName LastName" "NickName LastName" and "Prefix LastName" respectively.

2) drop

   An argument ``--drop-patterns``  points to the text file containing list of people to be dropped. Usually, this file is an ad hoc list of patterns that we want removed. For instance, patterns matching famous people not on the list.

3) editlength

   An argument ``--editlength`` contains minimum name length for the specific string length. For instance, ``--editlength 10 15`` means that for patterns of length 10 or more, match within edit distance of 1 and patterns of length 15 or more, match within edit distance of 2.

   If you want to disable `fuzzy` matching, just don't pass the argument ``--editlength``.


Usage
^^^^^

::

   usage: preprocess [-h] [-o OUTFILE] [-d DROP_PATTERNS_FILE]
                     [-p PATTERNS [PATTERNS ...]]
                     [-e EDITLENGTH [EDITLENGTH ...]]
                     input

   Preprocess Search List

   positional arguments:
   input                 Input file name

   optional arguments:
   -h, --help            show this help message and exit
   -o OUTFILE, --out OUTFILE
                           Output file in CSV (default:
                           deduped_augmented_clean_names.csv)
   -d DROP_PATTERNS_FILE, --drop-patterns DROP_PATTERNS_FILE
                           File with Default Patterns (default:
                           drop_patterns.txt)
   -p PATTERNS [PATTERNS ...], --patterns PATTERNS [PATTERNS ...]
                           List of Default Patterns (default: ['FirstName
                           LastName', 'NickName LastName', 'Prefix LastName'])
   -e EDITLENGTH [EDITLENGTH ...], --editlength EDITLENGTH [EDITLENGTH ...]
                           List of Edit Lengths (default: [])


Example
^^^^^^^

::

   preprocess augmented_clean_names.csv

By default, the output will be saved as ``deduped_augmented_clean_names.csv``. The script adds a new column, ``search_name`` for unique search key.


Search
~~~~~~~

We implement poor man's parallelization---scripts for splitting the corpus and merging the results back---along with multi-threading to quickly search through a large text corpus. We also provide the option to reduce the amount of searching by reducing the size of the text corpus by preprocessing it --- removing stop words etc.

There are three scripts --- to be run sequentially --- for the purpose:


Split text corpus into smaller chunks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This script splits large text corpora into multiple smaller chunks that can be run on multiple servers.

Usage
~~~~~

::

   usage: split_text_corpus [-h] [-o OUTFILE] [-s SIZE] input

   Split large text corpus into smaller chunks

   positional arguments:
   input                 CSV input file name

   optional arguments:
   -h, --help            show this help message and exit
   -o OUTFILE, --out OUTFILE
                           Output file in CSV (default:
                           chunk_{chunk_id:02d}/{basename}.csv)
   -s SIZE, --size SIZE  Number of row in each chunk (default: 1000)

Example
~~~~~~~

::

   split_text_corpus -s 1000 text_corpus.csv

The script will split `text_corpus.csv <https://github.com/appeler/search_names/blob/master/examples/search/text_corpus.csv>`__ into multiple ``chunk_*`` directories.

In this case ``chunk_00, chunk_01, ... chunk_09`` directory will be created along with ``text_corpus.csv`` which will have 1000 rows in it.

The output location and file name convention can be specified by the ``-o / --out`` command line option. Actually, it is a Python format string where ``chunk_id`` will replace chunk number starting from 0, and ``basename`` is input file's name (without path and extension).

Search for names
^^^^^^^^^^^^^^^^

This is the script to search names in the text corpus. The input file must contain at least two columns ``uniqid`` and ``text``.

Usage
~~~~~

::

   usage: search_names [-h] [-m MAX_NAME] [-p PROCESSES] [-o OUTFILE] [-t TEXT]
                     [-i INPUT_COLS [INPUT_COLS ...]]
                     [-c SEARCH_COLS [SEARCH_COLS ...]] [--overwritten]
                     [-e EDITLENGTH [EDITLENGTH ...]] [-f NAMEFILE]
                     [-u NAME_ID] [-s NAME_SEARCH] [-d] [--clean]
                     input

   Search names in text corpus

   positional arguments:
   input                 CSV input file name

   optional arguments:
   -h, --help            show this help message and exit
   -m MAX_NAME, --max-name MAX_NAME
                           Maximum name in search results (default: 20)
   -p PROCESSES, --processes PROCESSES
                           Number of processes to run (default: 4)
   -o OUTFILE, --out OUTFILE
                           Search results in CSV (default: search_results.csv)
   -t TEXT, --text TEXT  Column name with text (default: text)
   -i INPUT_COLS [INPUT_COLS ...], --input-cols INPUT_COLS [INPUT_COLS ...]
                           List of column name from input file to include in the
                           output (default: ['uniqid', 'text'])
   -c SEARCH_COLS [SEARCH_COLS ...], --search-cols SEARCH_COLS [SEARCH_COLS ...]
                           List of column name from search output (default:
                           ['uniqid', 'n', 'match', 'start', 'end', 'count'])
   --overwritten         Overwritten if output file is exists
   -e EDITLENGTH [EDITLENGTH ...], --editlength EDITLENGTH [EDITLENGTH ...]
                           List of Edit Lengths (default: [])
   -f NAMEFILE, --file NAMEFILE
                           CSV file contains unique ID and Name want to search
                           for (default: deduped_augmented_clean_names.csv)
   -u NAME_ID, --uniqid NAME_ID
                           Column of unique ID in name want to search for
                           (default: uniqid)
   -s NAME_SEARCH, --search NAME_SEARCH
                           Colunm of name want to search for (default:
                           search_name)
   -d, --debug           Enable debug message
   --clean               Clean text column before search

Arguments
~~~~~~~~~

- ``--search-cols`` that lists the columns from search file to be included in the output
- ``--input-cols`` that lists columns from the file containing the text data to be included in the output.
- ``--file`` which you can use to specify a CSV file where ``id`` and ``search`` refer to uniqid and keywords to be searched in that file respectively. In this case ``id`` and ``search`` are set to ``uniqid`` and ``search_name``\ , the de-duped output generated by `preprocess`_.
- ``--editlength`` specifies the list of minimum string length for that edit distance. For instance ``--editlength 10 15`` first value (``10``) means edit distance of 1 is allowed if string longer than 10 characters and the 2nd value (``15``) means that edit distance of 2 is allowed if the string is longer than 15 characters. We must use the same ``editlength`` as setting used in `preprocess`_ to avoid getting ambiguous search results. Once again, if you want to disable `fuzzy` matching, just omitted ``editlength``.
- ``--text`` specifies the name of the column that contains the text data to be searched.
- ``-m / --max-name`` is used to limit maximum search results.
- ``--overwritten`` is used to overwrite the output file if it exists; it is disabled by default.
- ``--clean`` option is provided to clean the ``text`` column (remove stop words, special characters etc.) before search.

Example
~~~~~~~

::

   search_names text_corpus.csv

By default, the script forks 4 processes (specify by ``-p / --processes``\ ) and searches for the names specified by ``--file``, ``--search``.

The output file (specify by ``-o / --out``\ ) will contains all columns from the input file (except ``text`` column will be replaced by cleaned text if ``--clean`` is specify) along with the search result columns that are:

::

   `nameX.uniqid` - uniqid number from name file
   `nameX.n` - occurrences of name found
   `nameX.match` - name found (separated by semi-colon `;` if multiple matches)
   `nameX.start` - start index of name found
   `nameX.end` - end index of name found
   `count` - total occurrences of name found


where ``X`` is result numbering start from 1 to maximum search results

Please note that row sequence in the output file will not be same as the input file as the script gets results from multi-threaded searching.

Merge Search Results
^^^^^^^^^^^^^^^^^^^^

Merge search results back from multiple files to a single file.

Usage
~~~~~

::

   usage: merge_results [-h] [-o OUTFILE] [inputs [inputs ...]]

   Merge search results from multiple chunks

   positional arguments:
   inputs                CSV input file(s) name

   optional arguments:
   -h, --help            show this help message and exit
   -o OUTFILE, --out OUTFILE
                           Output file in CSV (default:
                           merged_search_results.csv)


Example
~~~~~~~

::

   merge_results chunk_00/search_results.csv chunk_01/search_results.csv chunk_02/search_results.csv

Above script will merge 3 search results into a single output file. The default is ``merged_results.csv``

Documentation
-------------

For more information, please see `project documentation <http://search-names.readthedocs.io/en/latest/>`__.

Authors
-------

Suriyan Laohaprapanon and Gaurav Sood

Contributor Code of Conduct
---------------------------

The project welcomes contributions from everyone! In fact, it depends on
it. To maintain this welcoming atmosphere, and to collaborate in a fun
and productive way, we expect contributors to the project to abide by
the `Contributor Code of
Conduct <https://www.contributor-covenant.org/version/2/0/code_of_conduct/>`__.

License
-------

The package is released under the `MIT
License <https://opensource.org/licenses/MIT>`__.
