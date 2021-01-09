Search Names: Search a long list of names in a large text corpus
-----------------------------------------------------------------

.. image:: https://travis-ci.org/appeler/search-names.svg?branch=master
    :target: https://travis-ci.org/appeler/search-names
.. image:: https://ci.appveyor.com/api/projects/status/v3ao00u6uccnpi0n?svg=true
    :target: https://ci.appveyor.com/project/soodoku/search-names-hsmwu
.. image:: https://img.shields.io/pypi/v/search-names.svg
    :target: https://pypi.python.org/pypi/search-names
.. image:: https://readthedocs.org/projects/search-names/badge/?version=latest
    :target: http://search-names.readthedocs.io/en/latest/?badge=latest
.. image:: https://pepy.tech/badge/search-names
    :target: https://pepy.tech/project/search-names


There are seven kinds of challenges in searching a long list of names in a large text corpus: 

1. The names on the list may not be in a standard format, for e.g., first name may not always be followed by last
name, etc. 

2. It isn't clear what to search for. For instance, searching FirstName LastName may not be enough. References to the person
may take the form of Prefix LastName, etc. 

3. Names may be misspelled. 

4. Text may refer to people by their diminutive name (hypocorism), or by their middle name, or diminutive form of their
middle name, etc. For instance, citations to Bill Clinton are liable to be much more common than William Clinton. 

5. Names on the list may overlap with names not on the list, especially names of other famous
people. For instance, searching for `Maryland politician <https://en.wikipedia.org/wiki/Michael_A._Jackson_(politician)>`__
Michael Jackson may yield lots of false positives.

6. Names on the list may match other names on the list (duplicates).

7. Searching is computationally expensive. And searching for a long list over a large corpus is a double whammy.

We address each of the problems.

Before anything else, use `clean names <clean_names/>`__ to standardize
the names on the list. The script appends separate columns for prefix,
first\_name, last\_name, etc. Some human curation will likely still be
needed. Do it before going further. After that, use `merge supplementary
data <merge_supp_data/>`__ to append other potential prefixes,
diminutive norms of the first name, and other names by which the person
is known by to the output of `clean names <clean_names/>`__. Next,
`preprocess <preprocess/>`__ the search list. In particular, the script
does three things:

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

Lastly, the `search <search/>`__ script searches patterns in the list in
a multi-threaded, parallelized way.

The Workflow
~~~~~~~~~~~~

1. Clean Names
2. Merge Supplementary Data
3. Preprocess
4. Search

Installation
~~~~~~~~~~~~

We strongly recommend installing ``search-names`` inside a Python virtual environment (see `venv documentation <https://docs.python.org/3/library/venv.html#creating-virtual-environments>`__)

::

    pip install search-names

Functions
~~~~~~~~~~~~~~~~~~~~

``process_names``

The script is a modified version of `Clean Names <http://github.com/appeler/clean-names>`__.

The script takes a csv file with column 'Name' containing 'dirty names'--- names with all different formats: lastname firstname, firstname lastname, middlename lastname firstname etc. (see `sample input file <sample_input.csv>`_\ ) and produces a csv file that has all the columns of the original csv file and the following columns: 'uniqid', 'FirstName', 'MiddleInitial/Name', 'LastName', 'RomanNumeral', 'Title', 'Suffix' (see `sample output file <sample_output.csv>`_\ ).

Usage: ``process_names.py [options]``

Command Line Options
~~~~~~~~~~~~~~~~~~~~

.. code-block::

       -h,         --help show this help message and exit  
       -o OUTFILE, --out=OUTFILE  
                       Output file in CSV (default: sample_output.csv)  
       -c COLUMN,  --column=COLUMN  
                       Column name in CSV that contains Names (default: Name)    
       -a,         --all       
                   Export all names (do not take duplicate names out)  (default: False)

Example
~~~~~~~


.. raw:: html

   <pre><code> python process_names.py -a sample_input.csv </code></pre>

Merge Supplementary Data
~~~~~~~~~~~~~~~~~~~~~~~

The script takes output from `clean_names <../clean_names>`_ (see `sample input file <sample_in.csv>`_\ ) and appends supplementary data (prefixes, nicknames) to the file (see `sample output file <augmented_clean_names.csv>`_\ ). In particular, the script merges two supplementary data files:

   **Prefixes:** Generally the same set of prefixes will be used for a group of names. For instance, if you have a long list of politicians, state governors with no previous legislative experience will only have prefixes Governor, Mr., Mrs., Ms. etc., and not prefixes like Congressman or Congresswoman. We require a column in the input file that captures information about which 'prefix group' a particular name belongs to. We use that column to merge prefix data. The prefix file itself needs two columns: 1) A column to look up prefixes for groups of names depending on the value. The name of the column must be the same as the column name specified by the argument ``-p/--prefix`` (default is ``seat``\ ), and 2) a column of prefixes (multiple prefixes separated by semi-colon). The default name of the prefix data file is ``prefixes.csv``. See `sample prefixes data file <prefixes.csv>`_.   

   **Nicknames:**  Nicknames are merged using first names in the input data file. The nicknames file is a plain text file. Each line contains single or list of first names on left side of the '-' and one or multiple nicknames on the right hand side. List of first names and nicknames must be separated by comma. Default name of the nicknames data file is ``nick_names.txt``. See `sample nicknames file <nick_names.txt>`_.  

Usage
^^^^^

.. code-block::

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

Example
^^^^^^^

.. code-block::

   python merge_supp.py sample_in.csv

The script takes `sample_in.csv <sample_in.csv>`_\ , `prefixes.csv <prefixes.csv>`_\ , and `nick_names.txt <nick_names.txt>`_ and produces `augmented_clean_names.csv <augmented_clean_names.csv>`_. The output file has two additional columns:


* ``prefixes`` - List of prefixes (separated by semi-colon)  
* ``nick_names`` - List of nick names (separated by semi-colon)

Preprocess Search List
~~~~~~~~~~~~~~~~~~~~~~~

The script takes the output from `merge supp. data <../merge_supp_data/>`_ (\ `sample input file <augmented_clean_names.csv>`_\ ), list of patterns we want to search for, an ad hoc list of patterns we want to drop (\ `sample drop patterns file <drop_patterns.txt>`_\ , and relative edit distance (based on the length of the pattern we are searching for) for approximate matching and does three things: a) creates a row for each pattern we want to search for (duplicating all the supplementary information), b) drops the ad hoc list of patterns we want to drop and c) de-duplicates based on edit distance and patterns we want to search for. See `sample output file <deduped_augmented_clean_names.csv>`_.

The script relies on a configuration file, `\ ``preprocess.cfg`` <preprocess.cfg>`_\ , that allows users to describe the patterns to search for, name of the file containing patterns we want to drop, and edit distance.

Configuration file
^^^^^^^^^^^^^^^^^^

There are three sections in the `configuration file <preprocess.cfg>`_\ : 

1) search

This section contains patterns ---combination of field names---we want to search for:

.. code-block::

       [search]
       pattern1 = FirstName LastName
       pattern2 = NickName LastName
       pattern3 = Prefix LastName

2) drop

 The ``file`` variable points to the file containing list of people to be dropped. Usually, this file is an ad hoc list of patterns that we want removed. For instance, patterns matching famous people not on the list.

.. code-block::

       [drop]
       file = drop_patterns.txt

3) editlength

This section contains minimum name length for the specific string length. For instance, ``edit1=10`` means that for patterns of length 10 or more, match within edit distance of 1.

.. code-block::

       [editlength]
       edit1 = 10
       edit2 = 20

If you want to disable `fuzzy' matching, just comment out edit1 and edit2 using a hash sign as follows:

.. code-block::

   # edit1 = 10
   # edit2 = 20

Usage
^^^^^

.. code-block::

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

Example
^^^^^^^

.. code-block::

   python preprocess.py  augmented_clean_names.csv

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

.. code-block::

   usage: split_text_corpus.py [-h] [-o OUTFILE] [-s SIZE] input

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

.. code-block::

   python split_text_corpus.py -s 1000 text_corpus.csv

The script will split `\ ``text_corpus.csv`` <text_corpus.csv>`_ into multiple chunk_* directories.

In this case chunk_00, chunk_01, ... chunk_09 directory will be created along with ``text_corpus.txt`` which will have 1000 rows in it.

The output location and file name convention can be specified by the ``-o / --out`` command line option. Actually, it is a Python format string where ``chunk_id`` will replace chunk number starting from 0, and ``basename`` is input file's name (without path and extension).

Search for names
^^^^^^^^^^^^^^^^

This is the script to search names in the text corpus. The input file must contain at least two columns ``uniqid`` and ``text``.

Configuration file
~~~~~~~~~~~~~~~~~~

The script relies on a configuration file, `\ ``search_names.cfg`` <search_names.cfg>`_\ , `\ ``search_cols.txt`` <search_cols.txt>`_ that lists the columns from search file to be included in the output, and `\ ``input_file_cols.txt`` <input_file_cols.txt>`_ that lists columns from the file containing the text data to be included in the output.

The configuration file has three sections. In the ``[name]`` section of the configuration file, there is a variable ``file`` which you can use to specify a CSV file where ``id`` and ``search`` refer to uniqid and keywords to be searched in that file respectively. In this case ``id`` and ``search`` are set to ``uniqid`` and ``search_name``\ , the de-duped output generated by `preprocess <../preprocess/>`_. Section ``[editlength]`` specifies the minimum string length for that edit distance. ``edit1 = 10`` means edit distance of 1 is allowed if string longer than 10 characters and ``edit2 = 20`` means that edit distance of 2 is allowed if the string is longer than 20 characters. We must use the same ``editlength`` as `\ ``preprocess.cfg`` <../preprocess/preprocess.cfg>`_ to avoid getting ambiguous search results. ``text`` in the ``input`` section specifies the name of the column that contains the text data to be searched. 

.. code-block::

   [name]
   file = ../preprocess/deduped_augmented_clean_names.csv
   id = uniqid
   search = search_name

   [input]
   text = text

   [editlength]
   edit1 = 10
   edit2 = 20

Once again, if you want to disable `fuzzy' matching, just comment out edit1 and edit2 using a hash sign as follows:

.. code-block::

   # edit1 = 10
   # edit2 = 20

Usage
~~~~~

.. code-block::

   usage: search_names.py [-h] [-c CONFIG] [-m MAX_NAME] [-p PROCESSES]
                          [-o OUTFILE] [--overwritten] [-d] [--clean]
                          input

   Search names in text corpus

   positional arguments:
     input                 CSV input file name

   optional arguments:
     -h, --help            show this help message and exit
     -c CONFIG, --config CONFIG
                           Default configuration file (default: search_names.cfg)
     -m MAX_NAME, --max-name MAX_NAME
                           Maxinum name in search results (default: 20)
     -p PROCESSES, --processes PROCESSES
                           Number of multi-process to run (default: 4)
     -o OUTFILE, --out OUTFILE
                           Search results in CSV (default: search_results.csv)
     --overwritten         Overwritten if output file is exists
     -d, --debug           Enable debug message
     --clean               Clean text column before search

Example
~~~~~~~

.. code-block::

   python search_names.py text_corpus.csv

By default, the script forks 4 processes (specify by ``-p / --processes``\ ) and searches for the names specified by ``[name]`` section in the configuration file `\ ``search_names.cfg`` <search_names.cfg>`_. ``-m / --max-name`` is used to limit maximum search results. ``--overwritten`` is used to overwrite the output file if it exists; it is disabled by default. Also ``--clean`` option is provided to clean the ``text`` column (remove stop words, special characters etc.) before search. 

The output file (specify by ``-o / --out``\ ) will contains all columns from the input file (except ``text`` column will be replaced by cleaned text if ``--clean`` is specify) along with the search result columns that are:

.. code-block::

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

.. code-block::

   usage: merge_results.py [-h] [-o OUTFILE] [inputs [inputs ...]]

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

.. code-block::

   python merge_results.py chunk_00/search_results.csv chunk_01/search_results.csv chunk_02/search_results.csv

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
