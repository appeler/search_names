import sys
import warnings

if not sys.warnoptions:  # allow overriding with `-W` option
    warnings.filterwarnings('ignore', category=RuntimeWarning, module='runpy')

__version__ = "0.3.0"

# Initialize logging
from .logging_config import setup_logging

setup_logging()

from . import file_formats, models, nlp_engine
from .clean_names import clean_names
from .config import create_sample_config, get_config, get_config_manager, save_config
from .logging_config import get_logger, setup_logging
from .merge_results import merge_results
from .merge_supp import merge_supp
from .preprocess import preprocess
from .search_names import search_names
from .split_text_corpus import split_text_corpus

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
