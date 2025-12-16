# Search Names: Advanced Name Search and Entity Recognition

[![CI](https://github.com/appeler/search_names/workflows/CI/badge.svg)](https://github.com/appeler/search_names/actions?query=workflow%3ACI)
[![PyPI version](https://img.shields.io/pypi/v/search-names.svg)](https://pypi.org/project/search-names/)
[![Python versions](https://img.shields.io/pypi/pyversions/search-names.svg)](https://pypi.org/project/search-names/)
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
# Core installation (includes pandas, spaCy, sentence-transformers, CLI)
uv add search-names

# Or with pip
pip install search-names

# Optional: Advanced features (transformers, torch)
uv add "search-names[enhanced]"

# Optional: Additional formats (Parquet, Polars)
uv add "search-names[formats]"

# Optional: Search backends (Elasticsearch, OpenSearch)
uv add "search-names[search]"

# Optional: Web interface (FastAPI, Uvicorn)
uv add "search-names[web]"

# All optional features
uv add "search-names[all]"
```

### Modern CLI Interface

```bash
# Create sample configuration
search-names config create-sample

# Run complete pipeline
search-names pipeline input_names.csv text_corpus.csv

# Individual pipeline steps
search-names clean input_names.csv --streaming           # Step 1: Clean names
search-names merge-supp clean_names.csv                  # Step 2: Augment data
search-names preprocess augmented_names.csv              # Step 3: Preprocess
search-names search text_corpus.csv --optimized --streaming  # Step 4: Search

# Performance options
search-names search corpus.csv --optimized               # Use optimized search engine (default)
search-names search corpus.csv --streaming               # Memory-efficient streaming
search-names search corpus.csv --high-performance        # Best performance for large files
search-names search corpus.csv --processes 8             # Use 8 parallel processes
```

### Python API

```python
from search_names.pipeline import clean_names, augment_names, preprocess_names, search_names
from search_names.pipeline.step4_search import load_names_file
from search_names.config import get_config

# Load configuration
config = get_config()

# Step 1: Clean and standardize names
result = clean_names(
    infile="input_names.csv",
    outfile="clean_names.csv",
    col="Name",
    all=False  # Remove duplicates
)

# Step 2: Augment with supplementary data
augment_names(
    infile="clean_names.csv",
    prefixarg="seat",           # Column for prefix lookup
    name="FirstName",           # Column for nickname lookup
    outfile="augmented.csv",
    prefix_file="prefixes.csv",
    nickname_file="nick_names.txt"
)

# Step 3: Create optimized search patterns
preprocess_names(
    infile="augmented.csv",
    patterns=["FirstName LastName", "NickName LastName"],
    outfile="preprocessed.csv",
    editlength=[10, 15],        # Fuzzy matching lengths
    drop_patterns=["common", "the"]  # Patterns to exclude
)

# Step 4: High-performance search with optimization
names = load_names_file("preprocessed.csv")
result = search_names(
    input="text_corpus.csv",
    text="text",               # Text column name
    names=names,               # Preprocessed name list
    outfile="results.csv",
    use_optimized=True,        # Use vectorized search engine
    use_streaming=True,        # Memory-efficient for large files
    processes=8,               # Parallel processing
    max_name=20,               # Max results per document
    clean=True                 # Clean text before search
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
- **Multi-threaded parallel processing** with optimized chunking
- **High-performance mode** for large files (2-5x faster)
- **Fuzzy matching** with edit distance
- **Streaming mode** for memory efficiency
- Context-aware filtering and confidence scoring

**Input**: Text corpus + search patterns
**Output**: Ranked search results with confidence scores

## 🔧 Modern Features

### Advanced NLP Integration
- **spaCy NER**: Context-aware person detection
- **Transformers**: Semantic similarity matching
- **Entity Linking**: Connect mentions to knowledge bases
- **Confidence Scoring**: Quantify match uncertainty

### Performance & Scalability
- **Optimized Search Engine**: Vectorized string matching with NumPy
- **Streaming Processing**: Handle datasets larger than memory with chunking
- **Parallel Search**: Multi-process search with configurable worker count
- **Memory Management**: Automatic streaming for large files (>500MB)
- **Regex Optimization**: Pre-compiled patterns and single-pass matching
- **Early Termination**: Stop processing when result limits reached

### Developer Experience
- **Type Hints**: Full type annotation support
- **Rich Logging**: Beautiful, structured logging
- **Configuration**: YAML-based configuration management
- **Modern CLI**: Interactive command-line interface with progress bars

## 📁 File Format Support

| Format | Input | Output | Description |
|--------|-------|--------|-------------|
| CSV | ✅ | ✅ | Primary format with full pipeline support |
| Compressed CSV | ✅ | ✅ | Gzip-compressed CSV files (.csv.gz) |
| Text Files | ✅ | ❌ | Nickname/pattern lookup files (.txt) |

**Note**: Focus on CSV format ensures maximum compatibility and performance. Optional formats like Parquet and JSON can be added via the `[all]` installation option if needed.

## ⚡ Performance Optimizations

The package includes several performance optimizations for handling large-scale data:

### Automatic Streaming
```bash
# Files >500MB automatically use streaming
search-names search large_corpus.csv --optimized

# Force streaming for any file size
search-names clean names.csv --streaming
search-names search corpus.csv --streaming
```

### Optimized Search Engine
```python
from search_names.engines import create_optimized_search_engine

# Optimized implementation with better performance
engine = create_optimized_search_engine(names)
results = engine.search("sample text", max_results=10)
```

### Memory Management
- **Chunked Processing**: Processes files in 1000-row chunks by default
- **Progress Tracking**: Real-time progress reporting for long operations
- **Memory Estimation**: Automatic file size analysis to choose processing method
- **Resource Cleanup**: Proper cleanup of temporary files and memory

### Performance Monitoring
```python
import time
from search_names.engines import create_search_engine

# Compare basic vs optimized engines
basic_engine = create_search_engine(names, engine_type="basic")
optimized_engine = create_search_engine(names, engine_type="optimized")

# Time comparison
start = time.time()
basic_results = basic_engine.search(test_text)
basic_time = time.time() - start

start = time.time()
optimized_results = optimized_engine.search(test_text)
optimized_time = time.time() - start

print(f"Performance improvement: {basic_time/optimized_time:.1f}x faster")
```

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
  chunk_size: 1000
  timeout_seconds: 300

# Name cleaning
name_cleaning:
  default_patterns:
    - "FirstName LastName"
    - "NickName LastName"
    - "Prefix LastName"

# Text processing
text_processing:
  remove_stopwords: true
  normalize_unicode: true
  remove_punctuation: true
  language: "english"

# NLP features (optional)
nlp:
  use_spacy: false
  spacy_model: "en_core_web_sm"
  use_transformers: false
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  similarity_threshold: 0.8

# File handling
files:
  default_output_dir: "./output"
  encoding: "utf-8"
  csv_delimiter: ","

# Logging
log_level: "INFO"
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
from search_names.pipeline import clean_names

# Clean messy names
result = clean_names(
    infile="politicians.csv",
    outfile="clean_politicians.csv",
    col="Name",
    all=False  # Remove duplicates
)
print(f"Processed {len(result)} names")
```

### Advanced Search with Optimizations
```python
from search_names.pipeline import search_names
from search_names.pipeline.step4_search import load_names_file

# Load preprocessed names
names = load_names_file("politician_names.csv")

# Run optimized search
results = search_names(
    input="news_articles.csv",
    text="article_text",
    names=names,
    outfile="search_results.csv",
    max_name=50,
    processes=8,
    editlength=[8, 12],        # Fuzzy matching thresholds
    use_optimized=True,        # Use optimized engine (default)
    use_streaming=True,        # Stream large files
    use_high_performance=True, # Best performance for large files
    clean=True                 # Clean text preprocessing
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

We welcome contributions! Please see our [Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## 👥 Authors

- **Suriyan Laohaprapanon** - Original creator
- **Gaurav Sood** - Co-creator and maintainer

---

For detailed documentation and advanced usage, visit our [documentation site](https://appeler.github.io/search-names/).
