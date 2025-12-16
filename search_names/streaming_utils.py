#!/usr/bin/env python
"""
Streaming utilities for processing large files efficiently.

This module provides utilities for:
1. Chunked file processing to manage memory usage
2. Streaming CSV operations
3. Progress monitoring for large datasets
4. Memory-efficient data transformations
"""

import csv
import os
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

from .logging_config import get_logger

logger = get_logger("streaming_utils")

DEFAULT_CHUNK_SIZE = 1000
MAX_MEMORY_MB = 500  # Maximum memory usage before switching to streaming


class ChunkedCSVProcessor:
    """
    Process large CSV files in chunks to manage memory usage.
    """

    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE):
        """
        Initialize chunked CSV processor.

        Args:
            chunk_size: Number of rows to process at once
        """
        self.chunk_size = chunk_size
        self.stats = {
            "total_rows": 0,
            "chunks_processed": 0,
            "processing_time": 0,
        }

    def process_csv_in_chunks(
        self,
        input_file: str,
        output_file: str,
        processor_func: Callable[[list[dict]], list[dict]],
        progress_callback: Callable[[int], None] | None = None,
    ) -> dict:
        """
        Process a CSV file in chunks using a provided processing function.

        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file
            processor_func: Function that takes a list of row dicts and returns processed rows
            progress_callback: Optional callback function for progress updates

        Returns:
            Dictionary with processing statistics
        """
        start_time = time.time()

        with open(input_file, encoding="utf-8") as infile:
            reader = csv.DictReader(infile)

            # Write header first
            with open(output_file, "w", encoding="utf-8", newline="") as outfile:
                writer = None

                chunk = []
                for row in reader:
                    chunk.append(row)
                    self.stats["total_rows"] += 1

                    if len(chunk) >= self.chunk_size:
                        processed_chunk = processor_func(chunk)

                        # Initialize writer with first chunk's fieldnames
                        if writer is None:
                            if processed_chunk:
                                fieldnames = list(processed_chunk[0].keys())
                                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                                writer.writeheader()

                        # Write processed chunk
                        if writer and processed_chunk:
                            writer.writerows(processed_chunk)

                        self.stats["chunks_processed"] += 1
                        chunk = []

                        if progress_callback:
                            progress_callback(self.stats["total_rows"])

                        # Log progress
                        if self.stats["chunks_processed"] % 10 == 0:
                            elapsed = time.time() - start_time
                            rate = self.stats["total_rows"] / elapsed if elapsed > 0 else 0
                            logger.info(
                                f"Processed {self.stats['total_rows']} rows ({rate:.0f} rows/sec)"
                            )

                # Process remaining rows
                if chunk:
                    processed_chunk = processor_func(chunk)
                    if writer and processed_chunk:
                        writer.writerows(processed_chunk)
                    self.stats["chunks_processed"] += 1

        self.stats["processing_time"] = time.time() - start_time

        logger.info(
            f"Completed processing: {self.stats['total_rows']} rows in "
            f"{self.stats['processing_time']:.2f}s "
            f"({self.stats['total_rows'] / self.stats['processing_time']:.0f} rows/sec)"
        )

        return self.stats.copy()


def estimate_file_memory_usage(file_path: str) -> float:
    """
    Estimate memory usage for loading a CSV file.

    Args:
        file_path: Path to CSV file

    Returns:
        Estimated memory usage in MB
    """
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

    # Rough estimate: CSV in memory takes 2-3x file size
    estimated_memory_mb = file_size_mb * 2.5

    return estimated_memory_mb


def should_use_streaming(file_path: str, max_memory_mb: int = MAX_MEMORY_MB) -> bool:
    """
    Determine if streaming should be used based on file size.

    Args:
        file_path: Path to file to check
        max_memory_mb: Maximum memory usage threshold

    Returns:
        True if streaming should be used
    """
    estimated_mb = estimate_file_memory_usage(file_path)
    return estimated_mb > max_memory_mb


class StreamingCSVWriter:
    """
    Memory-efficient CSV writer for large datasets.
    """

    def __init__(self, output_file: str, fieldnames: list[str]):
        """
        Initialize streaming CSV writer.

        Args:
            output_file: Path to output file
            fieldnames: List of column names
        """
        self.output_file = output_file
        self.fieldnames = fieldnames
        self.rows_written = 0
        self._file = None
        self._writer = None

    def __enter__(self):
        """Enter context manager."""
        self._file = open(self.output_file, "w", encoding="utf-8", newline="")
        self._writer = csv.DictWriter(self._file, fieldnames=self.fieldnames)
        self._writer.writeheader()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if self._file:
            self._file.close()

    def writerow(self, row: dict) -> None:
        """Write a single row."""
        if self._writer:
            self._writer.writerow(row)
            self.rows_written += 1

    def writerows(self, rows: list[dict]) -> None:
        """Write multiple rows."""
        if self._writer:
            self._writer.writerows(rows)
            self.rows_written += len(rows)


def split_large_file(
    input_file: str, max_rows_per_file: int = 10000, output_dir: str | None = None
) -> list[str]:
    """
    Split a large CSV file into smaller files for parallel processing.

    Args:
        input_file: Path to input CSV file
        max_rows_per_file: Maximum rows per split file
        output_dir: Directory for output files (default: temp directory)

    Returns:
        List of paths to split files
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp()

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    input_path = Path(input_file)
    split_files = []

    with open(input_file, encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        file_num = 1
        current_rows = 0
        current_writer = None
        current_file = None

        for row in reader:
            if current_rows == 0:
                # Start new file
                split_file_path = output_dir / f"{input_path.stem}_part{file_num:03d}.csv"
                current_file = open(split_file_path, "w", encoding="utf-8", newline="")
                current_writer = csv.DictWriter(current_file, fieldnames=reader.fieldnames)
                current_writer.writeheader()
                split_files.append(str(split_file_path))

            current_writer.writerow(row)
            current_rows += 1

            if current_rows >= max_rows_per_file:
                # Close current file and start new one
                current_file.close()
                current_rows = 0
                file_num += 1

        # Close last file
        if current_file:
            current_file.close()

    logger.info(f"Split {input_file} into {len(split_files)} files")
    return split_files


def merge_split_files(split_files: list[str], output_file: str) -> None:
    """
    Merge split CSV files back into a single file.

    Args:
        split_files: List of paths to split files
        output_file: Path to merged output file
    """
    if not split_files:
        logger.warning("No split files to merge")
        return

    # Get fieldnames from first file
    with open(split_files[0], encoding="utf-8") as first_file:
        reader = csv.DictReader(first_file)
        fieldnames = reader.fieldnames

    with open(output_file, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for split_file in split_files:
            with open(split_file, encoding="utf-8") as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    writer.writerow(row)

    logger.info(f"Merged {len(split_files)} files into {output_file}")


class ProgressTracker:
    """
    Track and report progress for long-running operations.
    """

    def __init__(self, total: int | None = None, description: str = "Processing"):
        """
        Initialize progress tracker.

        Args:
            total: Total number of items to process (if known)
            description: Description of the operation
        """
        self.total = total
        self.description = description
        self.processed = 0
        self.start_time = time.time()
        self.last_update = 0

    def update(self, count: int = 1) -> None:
        """Update progress counter."""
        self.processed += count
        current_time = time.time()

        # Update every second
        if current_time - self.last_update >= 1.0:
            self._log_progress()
            self.last_update = current_time

    def _log_progress(self) -> None:
        """Log current progress."""
        elapsed = time.time() - self.start_time
        rate = self.processed / elapsed if elapsed > 0 else 0

        if self.total:
            percent = (self.processed / self.total) * 100
            eta = (self.total - self.processed) / rate if rate > 0 else 0
            logger.info(
                f"{self.description}: {self.processed}/{self.total} "
                f"({percent:.1f}%) - {rate:.0f}/sec - ETA: {eta:.0f}s"
            )
        else:
            logger.info(f"{self.description}: {self.processed} - {rate:.0f}/sec")

    def finish(self) -> None:
        """Log completion."""
        elapsed = time.time() - self.start_time
        rate = self.processed / elapsed if elapsed > 0 else 0
        logger.info(
            f"{self.description} completed: {self.processed} items in "
            f"{elapsed:.2f}s ({rate:.0f}/sec)"
        )


# Convenience functions for common operations


def process_large_csv(
    input_file: str,
    output_file: str,
    processor_func: Callable[[list[dict]], list[dict]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    auto_streaming: bool = True,
) -> dict:
    """
    Process a CSV file with automatic streaming for large files.

    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        processor_func: Function to process each chunk of rows
        chunk_size: Number of rows per chunk
        auto_streaming: Automatically use streaming for large files

    Returns:
        Processing statistics
    """
    if auto_streaming and should_use_streaming(input_file):
        logger.info(
            f"Large file detected ({estimate_file_memory_usage(input_file):.1f}MB), using streaming"
        )
        processor = ChunkedCSVProcessor(chunk_size)
        return processor.process_csv_in_chunks(input_file, output_file, processor_func)
    else:
        # Process entire file in memory
        logger.info("Processing file in memory")
        with open(input_file, encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            all_rows = list(reader)

        processed_rows = processor_func(all_rows)

        if processed_rows:
            with open(output_file, "w", encoding="utf-8", newline="") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=list(processed_rows[0].keys()))
                writer.writeheader()
                writer.writerows(processed_rows)

        return {
            "total_rows": len(all_rows),
            "chunks_processed": 1,
            "processing_time": 0,
        }
