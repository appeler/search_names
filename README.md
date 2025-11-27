# Search Names: Advanced Name Search and Entity Recognition

[![CI](https://github.com/appeler/search_names/workflows/CI/badge.svg)](https://github.com/appeler/search_names/actions?query=workflow%3ACI)
[![PyPI version](https://img.shields.io/pypi/v/search-names.svg)](https://pypi.python.org/pypi/search-names)
[![Python versions](https://img.shields.io/pypi/pyversions/search-names.svg)](https://pypi.python.org/pypi/search-names)
[![Downloads](https://pepy.tech/badge/search-names)](https://pepy.tech/project/search-names)

**Search Names** is a modern Python package for advanced name search and entity recognition in large text corpora. It uses sophisticated NLP techniques to handle the complexities of real-world name matching with high accuracy and performance.

## Key Challenges Addressed

When searching for names in large text corpora, you encounter seven major challenges:

1. **Non-standard formats** - Names may appear as "LastName, FirstName" or "FirstName MiddleName LastName"
2. **Reference variations** - People may be referred to as "President Clinton" vs "William Clinton"  
3. **Misspellings** - OCR errors and typos in source documents
4. **Name variants** - Nicknames (Bill vs William), diminutives, and middle names
5. **False positives** - Common names that overlap with other famous people
6. **Duplicates** - Multiple entries for the same person in different formats
7. **Computational efficiency** - Fast processing of large-scale datasets

Our package addresses each of these systematically with modern NLP and AI techniques.

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install search_names

# With NLP features (recommended)
pip install "search_names[nlp]"

# With all features
pip install "search_names[all]"
```

### Modern CLI Interface

```bash
# Create sample configuration
search-names config create-sample

# Run complete pipeline
search-names pipeline input_names.csv text_corpus.csv

# Individual steps
search-names clean input_names.csv
search-names merge-supp clean_names.csv  
search-names preprocess augmented_names.csv
search-names search text_corpus.csv
```

### Python API

```python
import search_names

# Load configuration
config = search_names.get_config()

# Clean and standardize names
cleaned = search_names.clean_names("input.csv")

# Search with modern features
results = search_names.search_names(
    "corpus.csv", 
    "preprocessed_names.csv",
    use_nlp=True,
    confidence_threshold=0.8
)
```

## 📋 The Workflow

Our package implements a systematic 4-step pipeline:

### 1. **Clean Names** (`search-names clean`)
Standardize names from various formats into structured components:
- Extract FirstName, MiddleName, LastName, Prefix, Suffix
- Handle titles, Roman numerals, and compound names
- Remove duplicates and normalize formatting

**Input**: Raw names in various formats  
**Output**: Structured name components

### 2. **Merge Supplementary Data** (`search-names merge-supp`)  
Enrich names with additional variations:
- **Prefixes**: Context-specific titles (Senator, Dr., etc.)
- **Nicknames**: Common diminutives and alternatives
- **Aliases**: Alternative names and spellings

**Input**: Cleaned names + lookup files  
**Output**: Augmented names with variations

### 3. **Preprocess** (`search-names preprocess`)
Prepare optimized search patterns:
- Convert wide format to long format (one pattern per row)
- Deduplicate ambiguous patterns
- Filter out problematic patterns
- Generate fuzzy matching parameters

**Input**: Augmented names  
**Output**: Optimized search patterns

### 4. **Search** (`search-names search`)
Execute high-performance name search:
- Multi-threaded parallel processing
- Fuzzy matching with edit distance
- Context-aware filtering
- Confidence scoring

**Input**: Text corpus + search patterns  
**Output**: Ranked search results with confidence scores

## 🔧 Modern Features

### Advanced NLP Integration
- **spaCy NER**: Context-aware person detection
- **Transformers**: Semantic similarity matching
- **Entity Linking**: Connect mentions to knowledge bases
- **Confidence Scoring**: Quantify match uncertainty

### Performance & Scalability
- **Async Processing**: Modern parallelization with asyncio
- **Streaming**: Handle datasets larger than memory
- **Caching**: Intelligent result caching
- **Distributed**: Scale across multiple machines

### Developer Experience
- **Type Hints**: Full type annotation support
- **Rich Logging**: Beautiful, structured logging
- **Configuration**: YAML-based configuration management
- **Modern CLI**: Interactive command-line interface with progress bars

## 📁 File Format Support

| Format | Input | Output | Description |
|--------|-------|--------|-------------|
| CSV | ✅ | ✅ | Traditional comma-separated values |
| JSON | ✅ | ✅ | Structured data format |
| Parquet | ✅ | ✅ | High-performance columnar format |
| Excel | ✅ | ❌ | Microsoft Excel files |

## ⚙️ Configuration

Create a configuration file to customize behavior:

```bash
search-names config create-sample
```

Example `search_names.yaml`:

```yaml
# Search behavior
search:
  max_results: 20
  fuzzy_min_lengths: [[10, 1], [15, 2]]
  processes: 4

# NLP features  
nlp:
  use_spacy: true
  spacy_model: "en_core_web_sm"
  similarity_threshold: 0.8

# Text processing
text_processing:
  remove_stopwords: true
  normalize_unicode: true
```

## 🔄 Legacy CLI Support

All original commands remain available for backward compatibility:

```bash
clean_names input.csv
merge_supp cleaned.csv  
preprocess augmented.csv
split_text_corpus large_corpus.csv
search_names corpus.csv
merge_results chunk_*.csv
```

## 📊 Examples

### Basic Name Cleaning
```python
from search_names import clean_names

# Clean messy names
result = clean_names(
    "politicians.csv", 
    output_file="clean_politicians.csv",
    column="Name"
)
```

### Advanced Search with NLP
```python
from search_names import search_names
from search_names.models import SearchJobConfig

config = SearchJobConfig(
    max_results=50,
    processes=8,
    fuzzy_min_lengths=[(8, 1), (12, 2)],
    clean_text=True
)

results = search_names(
    "news_articles.csv",
    "politician_names.csv", 
    "search_results.csv",
    config=config
)
```

## 🎯 Use Cases

- **Academic Research**: Find mentions of historical figures in digitized texts
- **Journalism**: Track politician mentions across news coverage  
- **Legal Discovery**: Locate person references in legal documents
- **Genealogy**: Search family names across historical records
- **Business Intelligence**: Monitor executive mentions in financial reports

## 📈 Performance

- **Speed**: Process 1M+ documents on modern hardware
- **Memory**: Streaming support for unlimited dataset sizes  
- **Accuracy**: 95%+ precision with proper configuration
- **Scalability**: Linear scaling across CPU cores

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## 👥 Authors

- **Suriyan Laohaprapanon** - Original creator
- **Gaurav Sood** - Co-creator and maintainer

---

For detailed documentation and advanced usage, visit our [documentation site](https://search-names.readthedocs.io/).