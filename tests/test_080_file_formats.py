#!/usr/bin/env python

"""
Tests for file_formats module
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

from search_names.file_formats import (
    FileFormatError,
    csv_to_json,
    csv_to_parquet,
    detect_file_format,
    get_file_info,
    json_to_csv,
    parquet_to_csv,
    read_file,
    read_file_chunked,
    write_file,
)


class TestFileFormatDetection(unittest.TestCase):
    """Test file format detection."""

    def test_detect_csv_format(self):
        """Test detection of CSV format."""
        self.assertEqual(detect_file_format("test.csv"), "csv")

    def test_detect_json_format(self):
        """Test detection of JSON formats."""
        self.assertEqual(detect_file_format("test.json"), "json")
        self.assertEqual(detect_file_format("test.jsonl"), "json")

    def test_detect_parquet_format(self):
        """Test detection of Parquet formats."""
        self.assertEqual(detect_file_format("test.parquet"), "parquet")
        self.assertEqual(detect_file_format("test.pq"), "parquet")

    def test_detect_excel_format(self):
        """Test detection of Excel formats."""
        self.assertEqual(detect_file_format("test.xlsx"), "excel")
        self.assertEqual(detect_file_format("test.xls"), "excel")

    def test_case_insensitive_detection(self):
        """Test that format detection is case insensitive."""
        self.assertEqual(detect_file_format("TEST.CSV"), "csv")
        self.assertEqual(detect_file_format("Test.JSON"), "json")

    def test_unsupported_format_error(self):
        """Test that unsupported formats raise FileFormatError."""
        with self.assertRaises(FileFormatError) as context:
            detect_file_format("test.txt")

        self.assertIn("Unsupported file format", str(context.exception))

    @patch('search_names.file_formats.HAS_PARQUET', False)
    def test_parquet_unavailable_error(self):
        """Test error when parquet format is requested but pyarrow unavailable."""
        with self.assertRaises(FileFormatError) as context:
            detect_file_format("test.parquet")

        self.assertIn("Parquet support requires pyarrow", str(context.exception))


class TestFileReading(unittest.TestCase):
    """Test file reading functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = pd.DataFrame({
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'age': [30, 25, 35],
            'city': ['New York', 'London', 'Paris']
        })

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_read_csv_file(self):
        """Test reading CSV files."""
        csv_path = Path(self.temp_dir) / "test.csv"
        self.test_data.to_csv(csv_path, index=False)

        df = read_file(csv_path)

        self.assertEqual(len(df), 3)
        self.assertListEqual(list(df.columns), ['name', 'age', 'city'])
        self.assertEqual(df.iloc[0]['name'], 'John Doe')

    def test_read_json_file(self):
        """Test reading JSON files."""
        json_path = Path(self.temp_dir) / "test.json"
        self.test_data.to_json(json_path, orient='records', lines=True)

        df = read_file(json_path)

        self.assertEqual(len(df), 3)
        self.assertIn('name', df.columns)

    def test_read_nonexistent_file_error(self):
        """Test that reading nonexistent file raises error."""
        nonexistent_path = Path(self.temp_dir) / "nonexistent.csv"

        with self.assertRaises(FileFormatError) as context:
            read_file(nonexistent_path)

        self.assertIn("File does not exist", str(context.exception))

    def test_auto_format_detection(self):
        """Test that file format is auto-detected when not specified."""
        csv_path = Path(self.temp_dir) / "test.csv"
        self.test_data.to_csv(csv_path, index=False)

        # Don't specify format - should auto-detect
        df = read_file(csv_path, file_format=None)

        self.assertEqual(len(df), 3)

    @patch('search_names.file_formats.HAS_POLARS', True)
    @patch('search_names.file_formats.pl')
    def test_read_with_polars_engine(self, mock_pl):
        """Test reading with polars engine."""
        mock_df = MagicMock()
        mock_df.to_pandas.return_value = self.test_data
        mock_pl.read_csv.return_value = mock_df

        csv_path = Path(self.temp_dir) / "test.csv"
        self.test_data.to_csv(csv_path, index=False)

        read_file(csv_path, engine="polars")

        mock_pl.read_csv.assert_called_once()
        mock_df.to_pandas.assert_called_once()


class TestFileWriting(unittest.TestCase):
    """Test file writing functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = pd.DataFrame({
            'name': ['John Doe', 'Jane Smith'],
            'age': [30, 25]
        })

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_write_csv_file(self):
        """Test writing CSV files."""
        csv_path = Path(self.temp_dir) / "output.csv"

        write_file(self.test_data, csv_path)

        self.assertTrue(csv_path.exists())

        # Verify content
        df_read = pd.read_csv(csv_path)
        self.assertEqual(len(df_read), 2)
        self.assertEqual(df_read.iloc[0]['name'], 'John Doe')

    def test_write_json_file(self):
        """Test writing JSON files."""
        json_path = Path(self.temp_dir) / "output.json"

        write_file(self.test_data, json_path)

        self.assertTrue(json_path.exists())

        # Verify content
        df_read = pd.read_json(json_path, lines=True)
        self.assertEqual(len(df_read), 2)

    def test_write_creates_directories(self):
        """Test that writing creates necessary directories."""
        nested_path = Path(self.temp_dir) / "subdir1" / "subdir2" / "output.csv"

        write_file(self.test_data, nested_path)

        self.assertTrue(nested_path.exists())
        self.assertTrue(nested_path.parent.exists())

    @patch('search_names.file_formats.HAS_PARQUET', True)
    def test_write_parquet_file(self):
        """Test writing Parquet files."""
        parquet_path = Path(self.temp_dir) / "output.parquet"

        with patch('pandas.DataFrame.to_parquet') as mock_to_parquet:
            write_file(self.test_data, parquet_path)
            mock_to_parquet.assert_called_once()

    @patch('search_names.file_formats.HAS_PARQUET', False)
    def test_write_parquet_unavailable_error(self):
        """Test error when writing parquet without pyarrow."""
        parquet_path = Path(self.temp_dir) / "output.parquet"

        with self.assertRaises(FileFormatError) as context:
            write_file(self.test_data, parquet_path)

        self.assertIn("Parquet support requires pyarrow", str(context.exception))


class TestChunkedReading(unittest.TestCase):
    """Test chunked file reading."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # Create larger test dataset
        self.large_data = pd.DataFrame({
            'id': range(1000),
            'name': [f'Name_{i}' for i in range(1000)],
            'value': range(1000, 2000)
        })

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_chunked_csv_reading(self):
        """Test reading CSV file in chunks."""
        csv_path = Path(self.temp_dir) / "large.csv"
        self.large_data.to_csv(csv_path, index=False)

        chunks = []
        for chunk in read_file_chunked(csv_path, chunk_size=100):
            chunks.append(chunk)

        # Should have 10 chunks of 100 rows each
        self.assertEqual(len(chunks), 10)
        self.assertEqual(len(chunks[0]), 100)

        # Verify data integrity
        combined = pd.concat(chunks, ignore_index=True)
        self.assertEqual(len(combined), 1000)

    def test_chunked_json_reading(self):
        """Test reading JSON Lines file in chunks."""
        json_path = Path(self.temp_dir) / "large.json"
        self.large_data.to_json(json_path, orient='records', lines=True)

        chunks = list(read_file_chunked(json_path, chunk_size=200, file_format="json"))

        # Should have 5 chunks of 200 rows each
        self.assertEqual(len(chunks), 5)
        self.assertEqual(len(chunks[0]), 200)

    @patch('search_names.file_formats.HAS_PARQUET', True)
    @patch('search_names.file_formats.pq')
    def test_chunked_parquet_reading(self, mock_pq):
        """Test reading Parquet file in chunks."""
        parquet_path = Path(self.temp_dir) / "large.parquet"

        # Mock parquet file and batches
        mock_file = MagicMock()
        mock_batch = MagicMock()
        mock_batch.to_pandas.return_value = self.large_data.iloc[:100]
        mock_file.iter_batches.return_value = [mock_batch, mock_batch]
        mock_pq.ParquetFile.return_value = mock_file

        chunks = list(read_file_chunked(parquet_path, chunk_size=100, file_format="parquet"))

        self.assertEqual(len(chunks), 2)
        mock_pq.ParquetFile.assert_called_once_with(parquet_path)

    def test_unsupported_format_for_chunking(self):
        """Test that unsupported formats for chunking raise error."""
        excel_path = Path(self.temp_dir) / "test.xlsx"

        with self.assertRaises(FileFormatError) as context:
            list(read_file_chunked(excel_path, file_format="excel"))

        self.assertIn("Chunked reading not supported for format: excel", str(context.exception))


class TestFileInfo(unittest.TestCase):
    """Test file information functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = pd.DataFrame({
            'name': ['John', 'Jane', 'Bob'],
            'age': [30, 25, 35]
        })

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_get_file_info_csv(self):
        """Test getting file info for CSV file."""
        csv_path = Path(self.temp_dir) / "test.csv"
        self.test_data.to_csv(csv_path, index=False)

        info = get_file_info(csv_path)

        self.assertEqual(info['format'], 'csv')
        self.assertEqual(info['rows'], 3)
        self.assertEqual(info['columns'], 2)
        self.assertEqual(info['column_names'], ['name', 'age'])
        self.assertGreater(info['size_bytes'], 0)

    def test_get_file_info_nonexistent(self):
        """Test that getting info for nonexistent file raises error."""
        nonexistent_path = Path(self.temp_dir) / "nonexistent.csv"

        with self.assertRaises(FileFormatError) as context:
            get_file_info(nonexistent_path)

        self.assertIn("File does not exist", str(context.exception))

    @patch('search_names.file_formats.detect_file_format')
    def test_get_file_info_unsupported_format(self, mock_detect):
        """Test file info handling of unsupported formats."""
        mock_detect.side_effect = FileFormatError("Unsupported format")

        txt_path = Path(self.temp_dir) / "test.txt"
        txt_path.write_text("some content")

        info = get_file_info(txt_path)

        self.assertIsNone(info['format'])
        self.assertGreater(info['size_bytes'], 0)

    def test_large_file_handling(self):
        """Test that large files get special handling."""
        csv_path = Path(self.temp_dir) / "test.csv"
        self.test_data.to_csv(csv_path, index=False)

        with patch('search_names.file_formats.Path.stat') as mock_stat:
            # Mock file size > 100MB
            mock_stat.return_value.st_size = 200 * 1024 * 1024

            info = get_file_info(csv_path)

            self.assertEqual(info['rows'], "Large file - use chunked reading")


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience conversion functions."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = pd.DataFrame({
            'name': ['John', 'Jane'],
            'age': [30, 25]
        })

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_csv_to_json_conversion(self):
        """Test CSV to JSON conversion."""
        csv_path = Path(self.temp_dir) / "input.csv"
        json_path = Path(self.temp_dir) / "output.json"

        self.test_data.to_csv(csv_path, index=False)

        csv_to_json(csv_path, json_path)

        self.assertTrue(json_path.exists())
        df_json = pd.read_json(json_path, lines=True)
        self.assertEqual(len(df_json), 2)

    @patch('search_names.file_formats.HAS_PARQUET', True)
    def test_csv_to_parquet_conversion(self):
        """Test CSV to Parquet conversion."""
        csv_path = Path(self.temp_dir) / "input.csv"
        parquet_path = Path(self.temp_dir) / "output.parquet"

        self.test_data.to_csv(csv_path, index=False)

        with patch('pandas.DataFrame.to_parquet') as mock_to_parquet:
            csv_to_parquet(csv_path, parquet_path)
            mock_to_parquet.assert_called_once()

    def test_json_to_csv_conversion(self):
        """Test JSON to CSV conversion."""
        json_path = Path(self.temp_dir) / "input.json"
        csv_path = Path(self.temp_dir) / "output.csv"

        self.test_data.to_json(json_path, orient='records', lines=True)

        json_to_csv(json_path, csv_path)

        self.assertTrue(csv_path.exists())
        df_csv = pd.read_csv(csv_path)
        self.assertEqual(len(df_csv), 2)

    @patch('search_names.file_formats.HAS_PARQUET', True)
    @patch('pandas.read_parquet')
    def test_parquet_to_csv_conversion(self, mock_read_parquet):
        """Test Parquet to CSV conversion."""
        mock_read_parquet.return_value = self.test_data

        parquet_path = Path(self.temp_dir) / "input.parquet"
        csv_path = Path(self.temp_dir) / "output.csv"

        parquet_to_csv(parquet_path, csv_path)

        mock_read_parquet.assert_called_once_with(parquet_path)
        self.assertTrue(csv_path.exists())


class TestErrorHandling(unittest.TestCase):
    """Test error handling in file operations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_read_corrupted_file_error(self):
        """Test handling of corrupted file reading."""
        csv_path = Path(self.temp_dir) / "corrupted.csv"
        csv_path.write_text("invalid,csv,content\nwith,missing\n")

        # Should handle the error gracefully
        try:
            df = read_file(csv_path)
            # Pandas might still read this, just check it doesn't crash
            self.assertIsNotNone(df)
        except FileFormatError:
            # Or it might raise our custom error, which is fine
            pass

    def test_write_permission_error(self):
        """Test handling of write permission errors."""
        # Create a read-only directory
        readonly_dir = Path(self.temp_dir) / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        output_path = readonly_dir / "output.csv"

        try:
            with self.assertRaises(FileFormatError):
                write_file(pd.DataFrame({'a': [1]}), output_path)
        finally:
            # Cleanup - restore write permissions
            readonly_dir.chmod(0o755)


if __name__ == '__main__':
    unittest.main()
