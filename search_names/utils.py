#!/usr/bin/env python

import os
import re
import string
import unicodedata

import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import EnglishStemmer
from nltk.tokenize import wordpunct_tokenize

from .logging_config import get_logger

logger = get_logger("utils")
#from ntlk.tokenize import sent_tokenize
"""
1. Convert to lower case
2. Take out special characters
3. Take out stop words
4. Stem the text
5. Remove punctuation
6. Remove extra space
7. Handling input and output
"""


def lower(text):
    """change everything to lowercase
    """
    text = text.lower()
    return text


def to_lower_case(text):
    return lower(text)


def remove_accents(text):
    """Remove diacritics
    """
    nkfd_form = unicodedata.normalize('NFKD', text)
    text = "".join([c for c in nkfd_form if not unicodedata.combining(c)])

    text = re.sub(r'[\x80-\xFF]', '', text)

    return text


def remove_diacritics(text):
    return remove_accents(text)


def remove_special_chars(text):
    """remove all special characters except the period (.)
       comma (,) and question mark (?)
       for instance, ">", "~", ", $, |, etc.
    """
    schars = ''.join([a for a in string.punctuation if a not in ".,?"])

    text = re.sub(f'[{re.escape(schars)}]', '', text)
    return text


def remove_special_characters(text):
    return remove_special_chars(text)


def remove_extra_space(text):
    """Remove multiple occurrence of whitespaces
    """
    text = " ".join(text.split())
    return text


def remove_extra_white_space(text):
    return remove_extra_space(text)


def remove_stopwords(text, swords=None):
    """Remove stopwords
    """
    if swords is None:
        swords = stopwords.words('english')
    words = wordpunct_tokenize(text)
    words = [w for w in words if w not in swords]
    text = ' '.join(words)
    return text


def remove_punctuation(text):
    """Replace punctuation mark with space
    """
    text = re.sub(f'[{re.escape(string.punctuation)}]', '', text)
    return text


def stemmed(text, snowball=False):
    """Returns stemmed text
    """
    if snowball:
        st = EnglishStemmer()
    else:
        st = PorterStemmer()
    words = wordpunct_tokenize(text)
    words = [st.stem(w) for w in words]
    text = ' '.join(words)

    return text


def get_export_path(outdir, filename):
    """Returns export filename
    """
    try:
        relpath = os.path.relpath(filename)
    except:
        relpath = os.path.splitdrive(filename)[1]
    relpath = re.sub(r'^[\.|\\|\/]*', '', relpath)
    extdir = outdir + '/' + os.path.dirname(relpath)
    fname = extdir + '/' + os.path.basename(relpath)
    outputname = os.path.abspath(fname)
    return outputname


def is_exported(outdir, filename):
    """Check output file existing
    """
    fname = get_export_path(outdir, filename)
    return os.path.exists(fname)


def export(outdir, filename, text):
    """Export text to output filename (with directory)
    """
    fname = get_export_path(outdir, filename)
    logger.info(f"Exporting text: {fname}...")
    try:
        extdir = os.path.split(fname)[0]
        if not os.path.exists(extdir):
            os.makedirs(extdir)
        with open(fname, "w") as f:
            f.write(text.encode('ascii', 'ignore'))
        return True
    except:
        raise
    return False


def split_sentences(text):
    """Returns split sentences list and index of splitting point

       Reference:
       http://stackoverflow.com/questions/8465335/a-regex-for-extracting-
              sentence-from-a-paragraph-in-python
    """
    sentenceEnders = re.compile(r"""
        # Split sentences on whitespace between them.
        (?:               # Group for two positive lookbehinds.
          (?<=[.!?])      # Either an end of sentence punct,
        | (?<=[.!?]['"])  # or end of sentence punct and quote.
        )                 # End group of two positive lookbehinds.
        (?<!  Mr\.   )    # Don't end sentence on "Mr."
        (?<!  Mrs\.  )    # Don't end sentence on "Mrs."
        (?<!  Jr\.   )    # Don't end sentence on "Jr."
        (?<!  Dr\.   )    # Don't end sentence on "Dr."
        (?<!  Prof\. )    # Don't end sentence on "Prof."
        (?<!  Sr\.   )    # Don't end sentence on "Sr."
        (?<!  Sen\.  )
        (?<!  Ms\.   )
        (?<!  Rep\.  )
        (?<!  Gov\.  )
        \s+               # Split on whitespace between sentences.
        """, re.IGNORECASE | re.VERBOSE)
    sentenceList = sentenceEnders.split(text)
    st_index = [0]
    for s in sentenceEnders.finditer(text):
        st_index.append(s.start())
    return sentenceList, st_index


def init_nltk():
    nltk.data.path.append("./nltk_data")
    if not os.path.exists('./nltk_data/corpora/stopwords'):
        nltk.download('stopwords', './nltk_data')
    if not os.path.exists('./nltk_data/tokenizers/punkt'):
        nltk.download('punkt', './nltk_data')


if __name__ == "__main__":
    from .logging_config import setup_logging
    setup_logging()

    with open('./test/input-latin-1.txt') as f:
        text = ''.join(f.readlines())

    init_nltk()

    logger.info('-'*20 + 'ORIGINAL' + '-'*20)
    logger.info(text)
    text = re.sub(r'(\d+)\.(\d+)', r'\1DOT\2', text)
    logger.info(text)
    logger.info('-'*20 + 'LOWER' + '-'*20)
    text = lower(text)
    logger.info(text)
    logger.info('-'*20 + 'Remove special chars' + '-'*20)
    text = remove_special_chars(text)
    logger.info(text)
    logger.info('-'*20 + 'Remove accents' + '-'*20)
    text = remove_accents(text)
    logger.info(text)
    logger.info('-'*20 + 'Remove stopwords' + '-'*20)
    text = remove_stopwords(text)
    logger.info(text)
    logger.info('-'*20 + 'Stemmed' + '-'*20)
    text = stemmed(text)
    logger.info(text)
    text = re.sub(r"\s\.", '.', text)
    text = re.sub(r'(\d+)dot(\d+)', r'\1.\2', text)
    logger.info(text)
    logger.info('-'*20 + 'Split sentences' + '-'*20)
    st, idx = split_sentences(text)
    logger.info(f"{st}, {idx}")
    #st = sent_tokenize(text)
    #print st
    logger.info('-'*20 + 'Remove punctuation' + '-'*20)
    text = remove_punctuation(text)
    logger.info(text)
    logger.info('-'*20 + 'Remove extra spaces' + '-'*20)
    text = remove_extra_space(text)
    logger.info(text)
    export('./test/output', './test/input.txt', text)
