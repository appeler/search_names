# Enhanced Name Parsing Examples

This directory demonstrates the enhanced name parsing capabilities of the modernized search_names package.

## Key Features

### Dual Parser Support
- **HumanName**: Rule-based parser (default, always available)
- **parsernaam**: ML-based parser (optional, for complex names)
- **Auto-selection**: Intelligent choice based on name patterns

### Enhanced Capabilities
- Confidence scoring for all parsing results
- Automatic Indian name detection for ML parser selection
- Batch processing with pandas DataFrame integration
- Multiple output format support (CSV, JSON, Parquet)
- Robust error handling and graceful degradation

## Files

### `enhanced_name_parsing_demo.py`
Comprehensive demonstration script showing:
- Basic enhanced parsing with confidence scores
- Parser comparison (HumanName vs parsernaam vs auto)
- DataFrame integration and batch processing
- Error handling for edge cases
- Configuration options
- Multiple output formats

### `sample_political_names.csv`
Sample dataset with political candidate names for testing, including:
- Traditional Western names with various formats
- Indian names that benefit from ML parsing
- Complex names with titles, suffixes, hyphens
- Edge cases for testing robustness

## Usage

### Basic Usage
```python
from search_names.enhanced_name_parser import NameParser

# Create parser with auto-selection
parser = NameParser(parser_type="auto")

# Parse a single name
result = parser.parse("Rajesh Kumar Sharma")
print(f"Name: {result.first_name} {result.last_name}")
print(f"Parser used: {result.parser_used}")
print(f"Confidence: {result.confidence}")
```

### DataFrame Processing
```python
import pandas as pd
from search_names.enhanced_name_parser import NameParser

# Load your data
df = pd.read_csv("sample_political_names.csv")

# Parse names and add components
parser = NameParser()
enhanced_df = parser.parse_dataframe(df, name_column="Name")

# Access parsed components
print(enhanced_df[['Name', 'parsed_first_name', 'parsed_last_name', 'parser_used']])
```

### Parser Comparison
```python
from search_names.enhanced_name_parser import compare_parsers

# Compare different parsers on the same name
results = compare_parsers("Rajesh Kumar Singh")
for parser_name, result in results.items():
    print(f"{parser_name}: {result.first_name} {result.last_name} (confidence: {result.confidence})")
```

## Running the Demo

```bash
# From the repository root
cd examples/enhanced_name_parsing
python enhanced_name_parsing_demo.py
```

This will run all demonstrations and create output files showing the enhanced parsing results.

## Improvements Over Legacy Approach

### Legacy (`clean_names.py`)
- Single parser (HumanName only)
- Basic error handling
- Limited configurability  
- Manual processing loops
- CSV output only

### Enhanced (current)
- Dual parser support with intelligent selection
- Confidence scoring and validation
- Comprehensive error handling with graceful degradation
- Flexible configuration options
- Modern pandas DataFrame integration
- Multiple output formats (CSV, JSON, Parquet)
- Type hints and modern Python features
- Rich logging instead of print statements

## Optional Dependencies

The enhanced parser works with just the base dependencies, but additional features are available with:

```bash
# For ML-based name parsing
pip install parsernaam

# For Parquet output support  
pip install pyarrow

# For full NLP features
pip install spacy sentence-transformers
python -m spacy download en_core_web_sm
```

The system gracefully degrades when optional dependencies are not available.