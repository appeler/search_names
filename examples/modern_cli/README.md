# Modern CLI Examples

This directory demonstrates the modernized CLI interface using typer instead of the legacy argparse approach.

## Key Features

### Modern CLI with Typer
- Rich help messages with markup
- Type-safe argument parsing
- Multiple subcommands
- Progress indicators and rich output
- Better error handling and user feedback

### Enhanced Functionality
- YAML configuration file support
- Multiple output formats (CSV, JSON, Parquet)
- Parser comparison capabilities
- Name validation and quality checking
- Batch processing with progress tracking

## Files

### `cli_demo.py`
Main CLI application demonstrating:
- `process-names`: Enhanced name processing with multiple options
- `compare-parsers`: Side-by-side parser comparison
- `generate-config`: Create sample configuration files
- `validate-names`: Check parsing quality and identify issues

### `sample_config.yaml` 
Example configuration file showing:
- Parser selection options
- Batch processing settings
- Confidence thresholds
- Logging configuration
- Output formatting preferences

## Usage Examples

### Basic Name Processing
```bash
# Process names with auto parser selection
python cli_demo.py process-names input.csv -o output.csv

# Use specific parser with JSON output
python cli_demo.py process-names input.csv -p parsernaam -f json -o output.json

# Use configuration file
python cli_demo.py process-names input.csv --config sample_config.yaml -o output.parquet
```

### Parser Comparison
```bash
# Compare parsing for specific names
python cli_demo.py compare-parsers "John Smith" "Rajesh Kumar Singh" "Dr. Mary Johnson-Brown"

# Save comparison results
python cli_demo.py compare-parsers "Complex Name" --save -o comparison.csv
```

### Configuration Management
```bash
# Generate sample configuration
python cli_demo.py generate-config -o my_config.yaml

# Process with custom configuration
python cli_demo.py process-names data.csv --config my_config.yaml
```

### Name Validation
```bash
# Validate parsing quality
python cli_demo.py validate-names input.csv --min-confidence 0.8

# Check specific column
python cli_demo.py validate-names data.csv -c "FullName" --min-confidence 0.7
```

## Command Reference

### `process-names`
Process names in CSV files with enhanced parsing.

**Arguments:**
- `input_file`: Input CSV file containing names

**Options:**
- `-o, --output`: Output file path (auto-detects format)
- `-c, --column`: Name column (default: "Name")
- `-p, --parser`: Parser type (humanname/parsernaam/auto)
- `--config`: YAML configuration file
- `-f, --format`: Output format (csv/json/parquet)
- `--confidence/--no-confidence`: Include confidence scores
- `--batch-size`: Batch size for processing
- `--ml-threshold`: ML confidence threshold

### `compare-parsers`
Compare parsing results across different parsers.

**Arguments:**
- `names`: List of names to parse and compare

**Options:**
- `--save`: Save comparison results to file
- `-o, --output`: Output file for results

### `generate-config`
Generate sample YAML configuration file.

**Options:**
- `-o, --output`: Output configuration file
- `--parser-type`: Default parser type
- `--batch-size`: Default batch size
- `--ml-threshold`: ML confidence threshold

### `validate-names`
Validate name parsing quality and identify issues.

**Arguments:**
- `input_file`: Input CSV file

**Options:**
- `-c, --column`: Name column to validate
- `--min-confidence`: Minimum confidence threshold

## Configuration File Format

```yaml
# Parser selection
parser_type: auto  # humanname, parsernaam, or auto

# Processing settings
batch_size: 100
ml_threshold: 0.8

# Logging
logging:
  level: INFO
  rich_logging: true

# Output formatting
output:
  include_confidence: true
  include_parser_info: true
  default_format: csv
```

## Improvements Over Legacy CLI

### Legacy Approach
- Basic argparse with limited help
- Single processing mode
- CSV output only
- Minimal error handling
- Print-based output

### Modern Approach
- Rich typer CLI with beautiful help
- Multiple subcommands and workflows
- Multiple output formats
- Comprehensive error handling
- Rich console output with tables and progress bars
- YAML configuration support
- Type safety and validation
- Extensible command structure

## Dependencies

Base requirements:
```bash
pip install typer rich pandas
```

Optional enhancements:
```bash
# For ML-based parsing
pip install parsernaam

# For Parquet output
pip install pyarrow

# For full configuration support
pip install pyyaml
```

## Integration with Package

The CLI can be integrated into the main package by adding entry points to `pyproject.toml`:

```toml
[project.scripts]
search-names = "search_names.cli:app"
```

This allows users to run the CLI directly:
```bash
search-names process-names input.csv -o output.json
```