import sys
import warnings

if not sys.warnoptions:  # allow overriding with `-W` option
    warnings.filterwarnings('ignore', category=RuntimeWarning, module='runpy')

__version__ = "0.3.0"

# Initialize logging
from .logging_config import setup_logging
setup_logging()

from .clean_names import clean_names
from .preprocess import preprocess
from .search_names import search_names
from .merge_results import merge_results
from .split_text_corpus import split_text_corpus
from .merge_supp import merge_supp
from .logging_config import setup_logging, get_logger
from .config import get_config, get_config_manager, save_config, create_sample_config
from . import models
from . import file_formats
from . import nlp_engine

__all__ = [
    'clean_names', 
    'preprocess', 
    'search_names', 
    'merge_results', 
    'searchengines', 
    'merge_supp', 
    'split_text_corpus',
    'setup_logging',
    'get_logger',
    'get_config',
    'get_config_manager',
    'save_config',
    'create_sample_config',
    'models',
    'file_formats',
    'nlp_engine',
]
