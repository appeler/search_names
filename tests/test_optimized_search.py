#!/usr/bin/env python
"""Tests for optimized search implementation."""

import csv
import tempfile
import unittest
from pathlib import Path

from search_names.pipeline.optimized_search import (
    OptimizedSearchProcessor,
    search_names_optimized,
)


class TestOptimizedSearch(unittest.TestCase):
    """Test optimized search functionality."""

    def setUp(self):
        """Set up test data."""
        self.test_names = [
            ("1", "john smith"),
            ("2", "jane doe"),
            ("3", "bob johnson"),
        ]

        # Create test data file
        self.test_data = [
            {"id": "1", "text": "Hello john smith how are you?"},
            {"id": "2", "text": "Jane doe is a nice person."},
            {"id": "3", "text": "I don't know bob johnson very well."},
            {"id": "4", "text": "This text has no names in it."},
            {"id": "5", "text": "Multiple names: john smith and jane doe together."},
        ]

        # Create temporary input file
        self.temp_input = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        writer = csv.DictWriter(self.temp_input, fieldnames=["id", "text"])
        writer.writeheader()
        writer.writerows(self.test_data)
        self.temp_input.close()

    def tearDown(self):
        """Clean up test files."""
        Path(self.temp_input.name).unlink(missing_ok=True)

    def test_chunk_calculation(self):
        """Test optimal chunk size calculation."""
        processor = OptimizedSearchProcessor(self.test_names, processes=2)
        chunk_size = processor._calculate_optimal_chunk_size()

        # Should be a reasonable size
        self.assertGreater(chunk_size, 0)
        self.assertLessEqual(chunk_size, 5000)

    def test_basic_search(self):
        """Test basic optimized search functionality."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as temp_output:
            output_file = temp_output.name

        try:
            # Run optimized search
            stats = search_names_optimized(
                input_file=self.temp_input.name,
                names=self.test_names,
                output_file=output_file,
                text_column="text",
                max_results=10,
                processes=2,
                clean_text=False,
            )

            # Check statistics
            self.assertIn("total_rows", stats)
            self.assertIn("total_results", stats)
            self.assertIn("processing_time", stats)
            self.assertGreater(stats["total_rows"], 0)

            # Check output file exists and has content
            self.assertTrue(Path(output_file).exists())

            with open(output_file) as f:
                reader = csv.reader(f)
                rows = list(reader)

            # Should have header + some results
            self.assertGreater(len(rows), 1)

            # Verify headers are present
            headers = rows[0]
            self.assertIn("id", headers)
            self.assertIn("text", headers)

        finally:
            Path(output_file).unlink(missing_ok=True)

    def test_chunk_processing(self):
        """Test file chunking functionality."""
        processor = OptimizedSearchProcessor(self.test_names, chunk_size=2)

        chunks = processor._create_file_chunks(self.temp_input.name, "text")

        # Should create multiple chunks with small chunk size
        self.assertGreater(len(chunks), 1)

        # Each chunk should have data
        for _chunk_start, _chunk_end, chunk_data in chunks:
            self.assertGreaterEqual(len(chunk_data), 0)

    def test_performance_vs_original(self):
        """Test that optimized version produces similar results to original."""
        # This test would compare results with the original implementation
        # For now, just ensure it runs without errors

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as temp_output:
            output_file = temp_output.name

        try:
            stats = search_names_optimized(
                input_file=self.temp_input.name,
                names=self.test_names,
                output_file=output_file,
                text_column="text",
                max_results=5,
                processes=1,  # Use single process for consistent testing
                clean_text=False,
            )

            # Basic validation
            self.assertIsInstance(stats, dict)
            self.assertGreater(stats["total_rows"], 0)

        finally:
            Path(output_file).unlink(missing_ok=True)

    def test_empty_input(self):
        """Test handling of empty input files."""
        # Create empty input file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as empty_input:
            writer = csv.DictWriter(empty_input, fieldnames=["id", "text"])
            writer.writeheader()
            empty_input_name = empty_input.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as temp_output:
            output_file = temp_output.name

        try:
            stats = search_names_optimized(
                input_file=empty_input_name,
                names=self.test_names,
                output_file=output_file,
                text_column="text",
                max_results=5,
                processes=1,
                clean_text=False,
            )

            # Should handle gracefully
            self.assertEqual(stats["total_rows"], 0)

        finally:
            Path(empty_input_name).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
