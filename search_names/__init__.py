import sys
import warnings
from importlib.metadata import version

from . import engines, models, nlp_engine
from .config import create_sample_config, get_config, get_config_manager, save_config
from .logging_config import get_logger, setup_logging
from .merge_results import merge_results
from .pipeline import clean_names, search_names
from .pipeline import preprocess_names as preprocess
from .pipeline.step2_augment import augment_names
from .split_text_corpus import split_text_corpus

# Backward compatibility aliases
merge_supp = augment_names

if not sys.warnoptions:  # allow overriding with `-W` option
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="runpy")

try:
    __version__ = version("search_names")
except Exception:
    __version__ = "unknown"

# Initialize logging after imports
setup_logging()

__all__ = [
    "clean_names",
    "preprocess",
    "search_names",
    "merge_supp",
    "merge_results",
    "split_text_corpus",
    "setup_logging",
    "get_logger",
    "get_config",
    "get_config_manager",
    "save_config",
    "create_sample_config",
    "engines",
    "models",
    "nlp_engine",
]
