import sys
import warnings

if not sys.warnoptions:  # allow overriding with `-W` option
    warnings.filterwarnings('ignore', category=RuntimeWarning, module='runpy')

from .process_names import process_names
from .preprocess import preprocess
from .search_names import search_names
from .merge_results import merge_results
from .split_text_corpus import split_text_corpus
from .merge_supp import merge_supp

__all__ = ['process_names', 'preprocess', 'search_names', 'merge_results', 'searchengines', 'merge_supp', 'split_text_corpus']
