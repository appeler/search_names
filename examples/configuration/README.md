# Configuration Examples

This directory demonstrates the configuration management capabilities of the modernized search_names package.

## Features

### YAML Configuration
- Centralized settings management
- Environment-specific configurations
- Type-safe configuration loading
- Validation and error handling

### Configuration Hierarchy
1. Default settings (built into package)
2. System-wide configuration (`/etc/search_names/config.yaml`)
3. User configuration (`~/.search_names/config.yaml`)
4. Project configuration (`./search_names.yaml`)
5. Environment variables
6. Command-line arguments

## Usage

### Load Configuration
```python
from search_names.config import get_config, load_config

# Load default configuration
config = get_config()

# Load from specific file
config = load_config("my_config.yaml")
```

### Save Configuration
```python
from search_names.config import save_config

save_config(config, "my_config.yaml")
```

### Generate Sample Configuration
```python
from search_names.config import create_sample_config

create_sample_config("sample_config.yaml")
```

## Configuration Options

See the example YAML files in this directory for complete configuration options covering:
- Name parsing settings
- Search parameters
- Logging configuration
- NLP model settings
- Output formatting
- Performance tuning
