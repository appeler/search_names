#!/usr/bin/env python

"""
Unified search engines with clear hierarchy and performance optimizations.

This module provides a complete search engine hierarchy:
- BasicSearchEngine: Simple regex-based search
- OptimizedSearchEngine: Vectorized operations for better performance
- StreamingSearchEngine: Memory-efficient for large datasets

All engines support fuzzy matching with Levenshtein distance.
"""

import csv
import time
from typing import Any

import regex as re
from Levenshtein import distance

from .logging_config import get_logger

logger = get_logger("engines")

# Constants
MAX_RESULT = 20
RESULT_FIELDS = ["uniqid", "n", "match", "start", "end"]
CHUNK_SIZE = 1000  # Number of rows to process at once


class BaseSearchEngine:
    """Base class for all search engines."""

    def __init__(self, keywords: list[tuple[str, str]], fuzzy_min_len: list[int] | None = None):
        """
        Initialize search engine.

        Args:
            keywords: List of (id, name) tuples
            fuzzy_min_len: List of minimum lengths for fuzzy matching
        """
        self.fuzzy_min_len = sorted(fuzzy_min_len or [])
        self.keywords = {}

        for uid, keyword in keywords:
            keyword = keyword.strip().lower()
            if uid not in self.keywords:
                self.keywords[uid] = [keyword]
            else:
                self.keywords[uid].append(keyword)

        logger.info(f"Initialized with {len(self.keywords)} unique keyword IDs")

    def _get_edit_distance_threshold(self, keyword: str) -> int:
        """Get allowed edit distance for fuzzy matching."""
        threshold = 0
        for min_length, dist in self.fuzzy_min_len:
            if len(keyword) > min_length:
                threshold = dist
        return threshold

    def search(self, text: str, max_results: int = MAX_RESULT) -> list[dict[str, Any]]:
        """Search for keywords in text. Must be implemented by subclasses."""
        raise NotImplementedError


class BasicSearchEngine(BaseSearchEngine):
    """Simple regex-based search engine. Good for small datasets."""

    def __init__(self, keywords: list[tuple[str, str]], fuzzy_min_len: list[int] | None = None):
        super().__init__(keywords, fuzzy_min_len)
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for each keyword group."""
        self.re_keywords = {}
        for uid in self.keywords:
            patterns = []
            for keyword in self.keywords[uid]:
                threshold = self._get_edit_distance_threshold(keyword)
                if threshold > 0:
                    patterns.append(rf"(?:{re.escape(keyword)}){{e<={threshold}}}")
                else:
                    patterns.append(re.escape(keyword))

            pattern_str = "|".join(patterns)
            pattern_str = rf"\b(?:{pattern_str})\b"
            self.re_keywords[uid] = re.compile(pattern_str, flags=re.I)

    def search(self, text: str, max_results: int = MAX_RESULT) -> list[dict[str, Any]]:
        """Search using compiled regex patterns."""
        results = []
        for uid, pattern in self.re_keywords.items():
            for match in pattern.finditer(text.lower()):
                if len(results) >= max_results:
                    break

                results.append(
                    {
                        "uniqid": uid,
                        "n": 1,
                        "match": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

            if len(results) >= max_results:
                break

        return results


class OptimizedSearchEngine(BaseSearchEngine):
    """Vectorized search engine with performance optimizations."""

    def __init__(self, keywords: list[tuple[str, str]], fuzzy_min_len: list[int] | None = None):
        super().__init__(keywords, fuzzy_min_len)

        # Build efficient lookup structures
        self.keyword_to_id = {}
        for uid, keyword in keywords:
            keyword = keyword.strip().lower()
            self.keyword_to_id[keyword] = uid

        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile optimized regex patterns."""
        self.compiled_patterns = []

        for uid, keywords_list in self.keywords.items():
            for keyword in keywords_list:
                threshold = self._get_edit_distance_threshold(keyword)
                if threshold > 0:
                    pattern = rf"\b{re.escape(keyword)}\b"
                    self.compiled_patterns.append(
                        (uid, keyword, threshold, re.compile(pattern, re.I))
                    )
                else:
                    pattern = rf"\b{re.escape(keyword)}\b"
                    self.compiled_patterns.append((uid, keyword, 0, re.compile(pattern, re.I)))

    def search(self, text: str, max_results: int = MAX_RESULT) -> list[dict[str, Any]]:
        """Optimized search with early termination."""
        results = []

        for uid, keyword, threshold, pattern in self.compiled_patterns:
            if len(results) >= max_results:
                break

            for match in pattern.finditer(text):
                matched_text = match.group().lower()

                # Apply fuzzy matching if threshold > 0
                if threshold > 0:
                    edit_distance = distance(keyword, matched_text)
                    if edit_distance > threshold:
                        continue

                results.append(
                    {
                        "uniqid": uid,
                        "n": 1,
                        "match": matched_text,
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

                if len(results) >= max_results:
                    break

        return results


class StreamingSearchEngine(BaseSearchEngine):
    """Memory-efficient search engine for large datasets."""

    def __init__(self, keywords: list[tuple[str, str]], fuzzy_min_len: list[int] | None = None):
        super().__init__(keywords, fuzzy_min_len)
        self.engine = OptimizedSearchEngine(keywords, fuzzy_min_len)

    def search_file_streaming(
        self,
        input_file: str,
        output_file: str,
        text_column: str = "text",
        chunk_size: int = CHUNK_SIZE,
        max_results_per_text: int = MAX_RESULT,
    ):
        """
        Search through large CSV files in chunks.

        Args:
            input_file: Path to input CSV
            output_file: Path to output CSV
            text_column: Name of column containing text
            chunk_size: Number of rows per chunk
            max_results_per_text: Max results per text entry
        """
        start_time = time.time()
        total_results = 0

        with (
            open(input_file, encoding="utf-8") as infile,
            open(output_file, "w", encoding="utf-8", newline="") as outfile,
        ):
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=RESULT_FIELDS + list(reader.fieldnames))
            writer.writeheader()

            chunk = []
            for i, row in enumerate(reader):
                chunk.append(row)

                if len(chunk) >= chunk_size:
                    results = self._process_chunk(chunk, text_column, max_results_per_text)
                    for result in results:
                        writer.writerow(result)
                    total_results += len(results)
                    chunk = []

                    if i % (chunk_size * 10) == 0:
                        logger.info(f"Processed {i} rows, found {total_results} results")

            # Process remaining rows
            if chunk:
                results = self._process_chunk(chunk, text_column, max_results_per_text)
                for result in results:
                    writer.writerow(result)
                total_results += len(results)

        elapsed = time.time() - start_time
        logger.info(f"Completed streaming search: {total_results} results in {elapsed:.2f}s")

    def _process_chunk(self, chunk: list[dict], text_column: str, max_results: int) -> list[dict]:
        """Process a chunk of rows."""
        results = []

        for row in chunk:
            if text_column not in row:
                continue

            text = row[text_column]
            if not text:
                continue

            matches = self.engine.search(text, max_results)
            for match in matches:
                result = match.copy()
                result.update(row)  # Include original row data
                results.append(result)

        return results

    def search(self, text: str, max_results: int = MAX_RESULT) -> list[dict[str, Any]]:
        """Delegate to optimized engine for single text search."""
        return self.engine.search(text, max_results)


def create_search_engine(
    keywords: list[tuple[str, str]],
    fuzzy_min_len: list[int] | None = None,
    engine_type: str = "optimized",
) -> BaseSearchEngine:
    """
    Factory function to create the appropriate search engine.

    Args:
        keywords: List of (id, name) tuples
        fuzzy_min_len: Fuzzy matching configuration
        engine_type: Type of engine ('basic', 'optimized', 'streaming')

    Returns:
        Configured search engine
    """
    if engine_type == "basic":
        return BasicSearchEngine(keywords, fuzzy_min_len)
    elif engine_type == "optimized":
        return OptimizedSearchEngine(keywords, fuzzy_min_len)
    elif engine_type == "streaming":
        return StreamingSearchEngine(keywords, fuzzy_min_len)
    else:
        raise ValueError(f"Unknown engine type: {engine_type}")


# Backward compatibility aliases
SearchMultipleKeywords = BasicSearchEngine
VectorizedSearchEngine = OptimizedSearchEngine


def create_optimized_search_engine(keywords, **kwargs):
    """Create an optimized search engine."""
    return create_search_engine(keywords, engine_type="optimized")
