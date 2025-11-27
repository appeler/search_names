"""Configuration management for search_names package."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .logging_config import get_logger

logger = get_logger("config")


@dataclass
class SearchConfig:
    """Configuration for search behavior."""

    max_results: int = 20
    fuzzy_min_lengths: list[list] = field(default_factory=lambda: [[10, 1], [15, 2]])
    edit_distances: list[int] = field(default_factory=list)
    processes: int = 4
    chunk_size: int = 1000
    timeout_seconds: int = 300


@dataclass
class NameCleaningConfig:
    """Configuration for name cleaning."""

    default_patterns: list[str] = field(
        default_factory=lambda: [
            "FirstName LastName",
            "NickName LastName",
            "Prefix LastName",
        ]
    )
    roman_numerals: list[str] = field(
        default_factory=lambda: [
            "I",
            "II",
            "III",
            "IV",
            "V",
            "VI",
            "VII",
            "VIII",
            "IX",
            "X",
        ]
    )
    drop_duplicates: bool = True
    parser_type: str = "auto"  # "humanname", "parsernaam", or "auto"
    batch_size: int = 100  # For parsernaam batch processing
    ml_threshold: float = 0.8  # Confidence threshold for ML predictions


@dataclass
class TextProcessingConfig:
    """Configuration for text preprocessing."""

    remove_stopwords: bool = True
    stemming: bool = False
    use_snowball_stemmer: bool = False
    remove_punctuation: bool = True
    remove_special_chars: bool = True
    normalize_unicode: bool = True
    language: str = "english"


@dataclass
class FileConfig:
    """Configuration for file I/O."""

    default_output_dir: str = "./output"
    input_formats: list[str] = field(default_factory=lambda: ["csv", "json", "parquet"])
    output_formats: list[str] = field(
        default_factory=lambda: ["csv", "json", "parquet"]
    )
    encoding: str = "utf-8"
    csv_delimiter: str = ","


@dataclass
class NLPConfig:
    """Configuration for NLP features."""

    use_spacy: bool = False
    spacy_model: str = "en_core_web_sm"
    use_transformers: bool = False
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    similarity_threshold: float = 0.8
    entity_linking: bool = False


@dataclass
class Config:
    """Main configuration class."""

    search: SearchConfig = field(default_factory=SearchConfig)
    name_cleaning: NameCleaningConfig = field(default_factory=NameCleaningConfig)
    text_processing: TextProcessingConfig = field(default_factory=TextProcessingConfig)
    files: FileConfig = field(default_factory=FileConfig)
    nlp: NLPConfig = field(default_factory=NLPConfig)

    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(message)s"
    rich_tracebacks: bool = True


class ConfigManager:
    """Manages configuration loading and saving."""

    def __init__(self, config_path: str | Path | None = None):
        self.config_path = (
            Path(config_path) if config_path else self._find_config_file()
        )
        self._config: Config | None = None

    def _find_config_file(self) -> Path | None:
        """Find configuration file in standard locations."""
        search_paths = [
            Path.cwd() / "search_names.yaml",
            Path.cwd() / "search_names.yml",
            Path.cwd() / ".search_names.yaml",
            Path.cwd() / ".search_names.yml",
            Path.home() / ".config" / "search_names" / "config.yaml",
            Path.home() / ".search_names.yaml",
        ]

        for path in search_paths:
            if path.exists():
                logger.info(f"Found configuration file: {path}")
                return path

        logger.debug("No configuration file found, using defaults")
        return None

    def load_config(self) -> Config:
        """Load configuration from file or use defaults."""
        if self._config is not None:
            return self._config

        config_dict = {}
        if self.config_path and self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    config_dict = yaml.safe_load(f) or {}
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.warning(f"Error loading config from {self.config_path}: {e}")
                logger.info("Using default configuration")

        # Create config with defaults and override with loaded values
        self._config = self._dict_to_config(config_dict)
        return self._config

    def save_config(self, config: Config, path: str | Path | None = None) -> None:
        """Save configuration to file."""
        save_path = Path(path) if path else self.config_path
        if not save_path:
            save_path = Path.cwd() / "search_names.yaml"

        # Ensure directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        config_dict = self._config_to_dict(config)

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            logger.info(f"Configuration saved to {save_path}")
            self.config_path = save_path
        except Exception as e:
            logger.error(f"Error saving config to {save_path}: {e}")
            raise

    def _dict_to_config(self, config_dict: dict[str, Any]) -> Config:
        """Convert dictionary to Config object."""

        # Helper function to create dataclass from dict
        def dict_to_dataclass(cls, data):
            if not isinstance(data, dict):
                return data

            # Get field names and types
            field_types = {f.name: f.type for f in cls.__dataclass_fields__.values()}
            kwargs = {}

            for key, value in data.items():
                if key in field_types:
                    # Handle nested dataclasses
                    field_type = field_types[key]
                    if hasattr(field_type, "__dataclass_fields__"):
                        kwargs[key] = dict_to_dataclass(field_type, value)
                    else:
                        kwargs[key] = value

            return cls(**kwargs)

        # Create main config
        config = Config()

        # Update with values from dict
        if "search" in config_dict:
            config.search = dict_to_dataclass(SearchConfig, config_dict["search"])
        if "name_cleaning" in config_dict:
            config.name_cleaning = dict_to_dataclass(
                NameCleaningConfig, config_dict["name_cleaning"]
            )
        if "text_processing" in config_dict:
            config.text_processing = dict_to_dataclass(
                TextProcessingConfig, config_dict["text_processing"]
            )
        if "files" in config_dict:
            config.files = dict_to_dataclass(FileConfig, config_dict["files"])
        if "nlp" in config_dict:
            config.nlp = dict_to_dataclass(NLPConfig, config_dict["nlp"])

        # Handle top-level config items
        for key in ["log_level", "log_format", "rich_tracebacks"]:
            if key in config_dict:
                setattr(config, key, config_dict[key])

        return config

    def _config_to_dict(self, config: Config) -> dict[str, Any]:
        """Convert Config object to dictionary."""

        def dataclass_to_dict(obj):
            if hasattr(obj, "__dataclass_fields__"):
                result = {}
                for field_name in obj.__dataclass_fields__:
                    value = getattr(obj, field_name)
                    result[field_name] = dataclass_to_dict(value)
                return result
            elif isinstance(obj, list):
                return [dataclass_to_dict(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: dataclass_to_dict(v) for k, v in obj.items()}
            else:
                return obj

        return {
            "search": dataclass_to_dict(config.search),
            "name_cleaning": dataclass_to_dict(config.name_cleaning),
            "text_processing": dataclass_to_dict(config.text_processing),
            "files": dataclass_to_dict(config.files),
            "nlp": dataclass_to_dict(config.nlp),
            "log_level": config.log_level,
            "log_format": config.log_format,
            "rich_tracebacks": config.rich_tracebacks,
        }


# Global config manager instance
_config_manager: ConfigManager | None = None


def get_config_manager(config_path: str | Path | None = None) -> ConfigManager:
    """Get the global configuration manager."""
    global _config_manager
    if _config_manager is None or config_path:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def get_config(config_path: str | Path | None = None) -> Config:
    """Get the current configuration."""
    return get_config_manager(config_path).load_config()


def save_config(config: Config, path: str | Path | None = None) -> None:
    """Save configuration to file."""
    get_config_manager().save_config(config, path)


def create_sample_config(path: str | Path = "search_names_sample.yaml") -> None:
    """Create a sample configuration file."""
    config = Config()  # Use defaults
    save_config(config, path)
    logger.info(f"Sample configuration created at {path}")
