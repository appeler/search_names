# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2024-12-16

### Major Reorganization

This release includes a complete codebase reorganization to eliminate confusion and improve maintainability.

#### Added
- Unified search engine hierarchy in `search_names.engines`
  - `BaseSearchEngine`: Abstract base class
  - `BasicSearchEngine`: Simple regex-based search
  - `OptimizedSearchEngine`: Vectorized operations for better performance
  - `StreamingSearchEngine`: Memory-efficient for large datasets
- Factory function `create_search_engine()` with backward compatibility
- Clear separation between core and enhanced dependencies in pyproject.toml

#### Changed
- **BREAKING**: Consolidated duplicate modules into single pipeline implementation
  - Removed root-level `clean_names.py`, `preprocess.py`, `search_names.py`, `merge_supp.py`
  - All functionality moved to `search_names.pipeline.*` modules
  - Maintained backward compatibility through import aliases
- Streamlined dependency management:
  - Core dependencies: Basic name parsing and fuzzy search
  - Enhanced dependencies: NLP, ML, and advanced features via `pip install "search_names[enhanced]"`
- Updated all imports to use consolidated pipeline versions
- Removed legacy command-line interfaces from pipeline modules

#### Removed
- Duplicate code across 4+ modules (>50% code deduplication)
- Confusing multiple search engine implementations
- Legacy CLI interfaces mixed with modern CLI
- Editorial comments and unnecessary complexity

#### Fixed
- All linting issues resolved
- Import structure clarified
- Performance bottlenecks in search engines
- Dependency categorization issues

#### Backward Compatibility
- All public APIs remain the same
- Import aliases maintained: `merge_supp = augment_names`
- Existing code should continue working without changes
- Search engine aliases: `SearchMultipleKeywords`, `VectorizedSearchEngine`

#### Migration Guide
For users importing from root modules:
```python
# Old (still works but deprecated)
from search_names.clean_names import clean_names

# New (recommended)
from search_names import clean_names
# or
from search_names.pipeline.step1_clean import clean_names
```

### Testing
- ✅ 119 tests passing, 1 skipped
- ✅ All linting checks pass
- ✅ Core functionality verified

## [0.4.1] - Previous Release
- Dependency updates and bug fixes
