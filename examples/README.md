# Search Names Package Examples

This directory contains comprehensive examples demonstrating the enhanced capabilities of the modernized search_names package (v0.4.0).

## 🎯 Overview

The examples showcase the transformation from a legacy command-line tool to a modern Python package with:
- **Dual parser support** (HumanName + parsernaam ML)
- **Intelligent auto-selection** based on name patterns
- **Rich NLP capabilities** with spaCy and transformers
- **Modern CLI interfaces** with typer and rich
- **Type-safe data processing** with pydantic validation
- **Multiple output formats** (CSV, JSON, Parquet)
- **Comprehensive configuration management**

## 📁 Example Categories

### 1. Enhanced Name Parsing (`enhanced_name_parsing/`)
**Core functionality with dual parser system**
- Intelligent parser selection (HumanName vs parsernaam)
- Confidence scoring and validation
- Indian name detection for ML parsing
- Batch processing with pandas DataFrames
- Error handling and graceful degradation

**Key Files:**
- `enhanced_name_parsing_demo.py` - Complete demonstration
- `sample_political_names.csv` - Test data
- `README.md` - Usage guide

### 2. Modern CLI Interface (`modern_cli/`)
**Next-generation command-line tools**
- Typer-based CLI with rich help messages
- YAML configuration file support
- Multiple output formats with auto-detection
- Parser comparison and validation tools
- Progress indicators and statistics

**Key Files:**
- `cli_demo.py` - Modern CLI application
- `sample_config.yaml` - Configuration template
- `README.md` - Command reference

### 3. NLP Features (`nlp_features/`)
**Advanced natural language processing**
- spaCy-based Named Entity Recognition
- Semantic similarity with sentence transformers
- Entity linking to knowledge bases
- Context-aware name search
- Complete NLP pipeline integration

**Key Files:**
- `nlp_demo.py` - NLP capabilities demonstration
- `README.md` - NLP usage guide
- Generated: `sample_knowledge_base.json`, `nlp_config.json`

### 4. Configuration Management (`configuration/`)
**Flexible, hierarchical configuration**
- YAML-based configuration files
- Environment-specific settings
- Type-safe configuration loading
- Validation and error handling
- Configuration inheritance hierarchy

**Key Files:**
- `README.md` - Configuration guide
- Examples of various configuration patterns

### 5. Integration Workflows (`integration_workflows/`)
**End-to-end production workflows**
- Complete name processing pipelines
- Multi-format data export workflows
- Batch processing optimization
- Error handling and recovery strategies
- Configuration-driven processing

**Key Files:**
- `complete_workflow_demo.py` - Full workflow demonstration
- `README.md` - Integration patterns

## 🚀 Quick Start

### Basic Usage
```python
from search_names.enhanced_name_parser import NameParser

# Auto-selecting parser (recommended)
parser = NameParser(parser_type="auto")
result = parser.parse("Rajesh Kumar Sharma")

print(f"Name: {result.first_name} {result.last_name}")
print(f"Parser used: {result.parser_used}")
print(f"Confidence: {result.confidence:.2f}")
```

### DataFrame Processing
```python
import pandas as pd
from search_names.enhanced_name_parser import NameParser

df = pd.read_csv("names.csv")
parser = NameParser()
enhanced_df = parser.parse_dataframe(df, name_column="Name")
```

### Modern CLI
```bash
# Process names with enhanced parsing
python modern_cli/cli_demo.py process-names input.csv -o output.json

# Compare different parsers
python modern_cli/cli_demo.py compare-parsers "John Smith" "Rajesh Kumar"

# Validate parsing quality
python modern_cli/cli_demo.py validate-names data.csv --min-confidence 0.8
```

## 🔧 Installation Requirements

### Base Package
```bash
pip install search_names
```

### Enhanced Features
```bash
# For ML-based name parsing
pip install 'search_names[ml]'

# For NLP capabilities
pip install 'search_names[nlp]'
python -m spacy download en_core_web_sm

# For all features
pip install 'search_names[all]'
```

## 📊 Feature Comparison

| Feature | Legacy (v0.3) | Enhanced (v0.4) |
|---------|---------------|-----------------|
| **Name Parsing** | HumanName only | HumanName + parsernaam ML |
| **Parser Selection** | Manual | Intelligent auto-selection |
| **Confidence Scoring** | ❌ | ✅ High-precision scoring |
| **DataFrame Support** | Basic | Full pandas integration |
| **Output Formats** | CSV only | CSV, JSON, Parquet |
| **CLI Interface** | argparse | Modern typer + rich |
| **Configuration** | Hardcoded | YAML-based, hierarchical |
| **NLP Features** | ❌ | spaCy NER + transformers |
| **Type Safety** | ❌ | Pydantic validation |
| **Error Handling** | Basic | Comprehensive + recovery |
| **Logging** | print() | Rich structured logging |
| **Testing** | Limited | Comprehensive test suite |

## 🎨 Key Improvements

### 1. **Intelligent Name Processing**
- **Auto-detection** of Indian names for ML parsing
- **Confidence scores** for all parsing results
- **Graceful degradation** when optional dependencies unavailable

### 2. **Modern Python Integration**
- **Type hints** throughout codebase
- **Pydantic models** for data validation
- **Rich logging** instead of print statements
- **Async support** for future scalability

### 3. **Production Ready**
- **Comprehensive error handling** with recovery strategies
- **Performance monitoring** and optimization
- **Memory efficient** batch processing
- **CI/CD integration** with GitHub Actions

### 4. **Developer Experience**
- **Rich help messages** with examples
- **Auto-completion** support
- **Progress indicators** for long operations
- **Detailed documentation** with working examples

## 🏃‍♂️ Running the Examples

### Individual Examples
```bash
# Enhanced name parsing
cd enhanced_name_parsing && python enhanced_name_parsing_demo.py

# Modern CLI features
cd modern_cli && python cli_demo.py --help

# NLP capabilities
cd nlp_features && python nlp_demo.py

# Complete workflows
cd integration_workflows && python complete_workflow_demo.py
```

### All Examples
```bash
# Run all example scripts
find examples -name "*.py" -path "*/demo.py" -exec python {} \;
```

## 🔮 Next Steps

After exploring these examples:

1. **Review the main README.md** for package overview
2. **Check the test suite** in `tests/` for comprehensive usage patterns
3. **Examine the source code** in `search_names/` for implementation details
4. **Configure your environment** using the configuration examples
5. **Integrate into your workflows** using the integration patterns

## 💡 Tips for Success

- **Start with `enhanced_name_parsing/`** to understand core concepts
- **Use `auto` parser type** for best results with mixed datasets
- **Configure logging levels** appropriate for your environment
- **Test with your data** using the validation tools
- **Leverage batch processing** for large datasets
- **Consider NLP features** for advanced use cases

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/appeler/search_names/issues)
- **Documentation**: Package README and example READMEs
- **Tests**: Comprehensive test suite in `tests/` directory

---

**search_names v0.4.0** - From legacy tool to modern Python package 🚀
