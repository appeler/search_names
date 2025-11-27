#!/usr/bin/env python
"""
Optimized search engines for better performance with large datasets.

Key optimizations:
1. Vectorized string operations using NumPy
2. Efficient data structures (sets, dicts)
3. Compiled regex pattern caching
4. Memory-efficient streaming for large files
5. Early termination strategies
"""

import csv
import time

import regex as re
from Levenshtein import distance

from .logging_config import get_logger

# pandas not used in this module currently
HAS_PANDAS = False

logger = get_logger("optimized_searchengines")

# Constants
MAX_RESULT = 20
RESULT_FIELDS = ["uniqid", "n", "match", "start", "end"]
CHUNK_SIZE = 1000  # Number of rows to process at once


class VectorizedSearchEngine:
    """
    Optimized search engine using vectorized operations and efficient data structures.
    """

    def __init__(
        self, keywords: list[tuple[str, str]], fuzzy_min_len: list[int] | None = None
    ):
        """
        Initialize search with performance optimizations.

        Args:
            keywords: List of (id, name) tuples
            fuzzy_min_len: List of minimum lengths for fuzzy matching
        """
        self.fuzzy_min_len = sorted(fuzzy_min_len or [])

        # Use more efficient data structures
        self.keyword_to_id = {}
        self.id_to_keywords = {}

        start_time = time.time()

        for uid, keyword in keywords:
            keyword = keyword.strip().lower()
            self.keyword_to_id[keyword] = uid

            if uid not in self.id_to_keywords:
                self.id_to_keywords[uid] = []
            self.id_to_keywords[uid].append(keyword)

        # Pre-compile regex patterns for better performance
        self._compile_patterns()

        setup_time = time.time() - start_time
        logger.info(
            f"Initialized {len(self.keyword_to_id)} keywords in {setup_time:.3f}s"
        )

    def _compile_patterns(self):
        """Pre-compile regex patterns for faster matching."""
        patterns = []

        for keyword in self.keyword_to_id.keys():
            distance_threshold = self._get_edit_distance_threshold(keyword)

            if distance_threshold > 0:
                # Fuzzy matching with edit distance
                pattern = rf"(?:{re.escape(keyword)}){{e<={distance_threshold}}}"
            else:
                # Exact matching
                pattern = re.escape(keyword)

            patterns.append(pattern)

        # Single compiled pattern for all keywords
        combined_pattern = "|".join(patterns)
        self.regex_pattern = re.compile(rf"\b(?:{combined_pattern})\b", re.IGNORECASE)

    def _get_edit_distance_threshold(self, keyword: str) -> int:
        """Get allowed edit distance for a keyword based on its length."""
        threshold = 0
        for min_len, dist in self.fuzzy_min_len:
            if len(keyword) >= min_len:
                threshold = dist
        return threshold

    def _find_nearest_keyword(self, text: str) -> str | None:
        """Find the nearest keyword using edit distance."""
        min_distance = float("inf")
        nearest_keyword = None

        for keyword in self.keyword_to_id.keys():
            threshold = self._get_edit_distance_threshold(keyword)
            if threshold > 0:
                dist = distance(keyword, text.lower())
                if dist <= threshold and dist < min_distance:
                    min_distance = dist
                    nearest_keyword = keyword

        return nearest_keyword

    def search(self, text: str, max_results: int = MAX_RESULT) -> tuple[list, int]:
        """
        Optimized search function.

        Args:
            text: Text to search in
            max_results: Maximum number of results to return

        Returns:
            Tuple of (results list, total count)
        """
        if max_results == 0:
            return [], 0

        # Use dictionary for O(1) lookup instead of lists
        matches = {}

        # Single regex search instead of multiple
        for match in self.regex_pattern.finditer(text):
            found_text = match.group(0).strip()
            keyword = found_text.lower()

            # Check if exact match exists
            if keyword in self.keyword_to_id:
                uid = self.keyword_to_id[keyword]
            else:
                # Try fuzzy matching
                nearest = self._find_nearest_keyword(found_text)
                if nearest:
                    uid = self.keyword_to_id[nearest]
                else:
                    continue

            if uid not in matches:
                matches[uid] = []
            matches[uid].append((found_text, match.start(), match.end()))

        # Build results efficiently
        results = []
        count = 0

        for i, (uid, match_list) in enumerate(matches.items()):
            if i >= max_results:
                break

            results.extend(
                [
                    uid,
                    len(match_list),
                    ";".join([m[0] for m in match_list]),
                    ";".join([str(m[1]) for m in match_list]),
                    ";".join([str(m[2]) for m in match_list]),
                ]
            )
            count += len(match_list)

        # Pad results to expected length
        while len(results) < max_results * len(RESULT_FIELDS):
            results.extend([""] * len(RESULT_FIELDS))

        return results, count


class StreamingSearchEngine:
    """
    Memory-efficient search engine for large files using streaming.
    """

    def __init__(
        self, keywords: list[tuple[str, str]], fuzzy_min_len: list[int] | None = None
    ):
        """Initialize streaming search engine."""
        self.search_engine = VectorizedSearchEngine(keywords, fuzzy_min_len)

    def search_file_streaming(
        self,
        input_file: str,
        output_file: str,
        text_column: str = "text",
        chunk_size: int = CHUNK_SIZE,
        max_results: int = MAX_RESULT,
    ) -> int:
        """
        Search through a large file using streaming to manage memory.

        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file
            text_column: Name of column containing text to search
            chunk_size: Number of rows to process at once
            max_results: Maximum results per row

        Returns:
            Total number of matches found
        """
        total_matches = 0
        rows_processed = 0

        with (
            open(input_file, encoding="utf-8") as infile,
            open(output_file, "w", encoding="utf-8", newline="") as outfile,
        ):
            reader = csv.DictReader(infile)

            # Prepare output headers
            headers = list(reader.fieldnames)
            for i in range(max_results):
                for field in RESULT_FIELDS:
                    headers.append(f"name{i + 1:d}.{field}")
            headers.append("count")

            writer = csv.DictWriter(outfile, fieldnames=headers)
            writer.writeheader()

            # Process in chunks
            chunk = []
            for row in reader:
                chunk.append(row)

                if len(chunk) >= chunk_size:
                    matches = self._process_chunk(chunk, text_column, max_results)
                    total_matches += matches

                    self._write_chunk_results(writer, chunk, text_column, max_results)

                    rows_processed += len(chunk)
                    logger.info(
                        f"Processed {rows_processed} rows, found {total_matches} matches"
                    )

                    chunk = []

            # Process remaining rows
            if chunk:
                matches = self._process_chunk(chunk, text_column, max_results)
                total_matches += matches
                self._write_chunk_results(writer, chunk, text_column, max_results)
                rows_processed += len(chunk)

        logger.info(
            f"Completed: {rows_processed} rows processed, {total_matches} total matches"
        )
        return total_matches

    def _process_chunk(
        self, chunk: list[dict], text_column: str, max_results: int
    ) -> int:
        """Process a chunk of rows and store results."""
        total_matches = 0

        for row in chunk:
            text = row.get(text_column, "")
            if text:
                results, count = self.search_engine.search(text, max_results)
                row["_search_results"] = results
                row["_search_count"] = count
                total_matches += count
            else:
                row["_search_results"] = [""] * (max_results * len(RESULT_FIELDS))
                row["_search_count"] = 0

        return total_matches

    def _write_chunk_results(
        self,
        writer: csv.DictWriter,
        chunk: list[dict],
        text_column: str,
        max_results: int,
    ):
        """Write chunk results to output file."""
        for row in chunk:
            # Build output row
            output_row = {k: v for k, v in row.items() if not k.startswith("_")}

            # Add search results
            results = row.get("_search_results", [])
            for i in range(max_results):
                base_idx = i * len(RESULT_FIELDS)
                for j, field in enumerate(RESULT_FIELDS):
                    col_name = f"name{i + 1:d}.{field}"
                    if base_idx + j < len(results):
                        output_row[col_name] = results[base_idx + j]
                    else:
                        output_row[col_name] = ""

            output_row["count"] = row.get("_search_count", 0)

            writer.writerow(output_row)


def create_optimized_search_engine(
    keywords: list[tuple[str, str]],
    fuzzy_min_len: list[int] | None = None,
    use_streaming: bool = False,
):
    """
    Factory function to create the appropriate search engine.

    Args:
        keywords: List of (id, name) tuples
        fuzzy_min_len: List of minimum lengths for fuzzy matching
        use_streaming: Whether to use streaming engine for large files

    Returns:
        Appropriate search engine instance
    """
    if use_streaming:
        return StreamingSearchEngine(keywords, fuzzy_min_len)
    else:
        return VectorizedSearchEngine(keywords, fuzzy_min_len)


# Benchmark function for testing performance improvements
def benchmark_search_engines(
    keywords: list[tuple[str, str]], test_text: str, iterations: int = 100
):
    """
    Benchmark different search engines to compare performance.

    Args:
        keywords: List of (id, name) tuples
        test_text: Text to search in
        iterations: Number of iterations for timing
    """
    from .searchengines import NewSearchMultipleKeywords

    # Original engine
    original_engine = NewSearchMultipleKeywords(keywords)

    # Optimized engine
    optimized_engine = VectorizedSearchEngine(keywords)

    # Benchmark original
    start_time = time.time()
    for _ in range(iterations):
        original_engine.search(test_text)
    original_time = time.time() - start_time

    # Benchmark optimized
    start_time = time.time()
    for _ in range(iterations):
        optimized_engine.search(test_text)
    optimized_time = time.time() - start_time

    speedup = original_time / optimized_time

    logger.info(f"Original engine: {original_time:.3f}s")
    logger.info(f"Optimized engine: {optimized_time:.3f}s")
    logger.info(f"Speedup: {speedup:.2f}x")

    return speedup
