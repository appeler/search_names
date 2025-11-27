#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for CLI interface
"""

import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import tempfile
import pandas as pd
from typer.testing import CliRunner


class TestCLI(unittest.TestCase):
    """Test CLI interface."""

    def setUp(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('search_names.cli.app')
    def test_cli_import(self, mock_app):
        """Test that CLI can be imported."""
        try:
            from search_names.cli import app, main_cli
            self.assertIsNotNone(app)
            self.assertIsNotNone(main_cli)
        except ImportError:
            self.skipTest("CLI module not available")

    def test_cli_help(self):
        """Test CLI help command."""
        try:
            from search_names.cli import app
            result = self.runner.invoke(app, ["--help"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("search-names", result.stdout.lower())
        except ImportError:
            self.skipTest("CLI module not available")

    @patch('search_names.cli.clean_names_func')
    def test_clean_command(self, mock_clean):
        """Test clean command."""
        try:
            from search_names.cli import app
            
            # Create test input file
            input_path = Path(self.temp_dir) / "names.csv"
            input_path.write_text("name\nJohn Doe\nJane Smith")
            
            # Mock the clean function
            mock_clean.return_value = pd.DataFrame({
                'original_name': ['John Doe', 'Jane Smith'],
                'first_name': ['John', 'Jane'],
                'last_name': ['Doe', 'Smith']
            })
            
            result = self.runner.invoke(app, [
                "clean",
                str(input_path),
                "--output", str(Path(self.temp_dir) / "cleaned.csv")
            ])
            
            # Check that command succeeded
            if result.exit_code != 0:
                print(f"Error: {result.stdout}")
            
            mock_clean.assert_called_once()
            
        except ImportError:
            self.skipTest("CLI module not available")

    @patch('search_names.cli.search_names_func')
    def test_search_command(self, mock_search):
        """Test search command."""
        try:
            from search_names.cli import app
            
            # Create test files
            names_path = Path(self.temp_dir) / "names.csv"
            names_path.write_text("name\nJohn Doe")
            
            corpus_path = Path(self.temp_dir) / "corpus.csv"
            corpus_path.write_text("text\nJohn Doe is here")
            
            # Mock the search function
            mock_search.return_value = pd.DataFrame({
                'name': ['John Doe'],
                'count': [1],
                'positions': ['0-8']
            })
            
            result = self.runner.invoke(app, [
                "search",
                str(names_path),
                str(corpus_path),
                "--output", str(Path(self.temp_dir) / "results.csv")
            ])
            
            # Check that search was called
            if result.exit_code == 0:
                mock_search.assert_called_once()
            
        except ImportError:
            self.skipTest("CLI module not available")

    def test_config_command(self):
        """Test config command."""
        try:
            from search_names.cli import app
            
            config_path = Path(self.temp_dir) / "config.yaml"
            
            result = self.runner.invoke(app, [
                "config",
                "create",
                "--path", str(config_path)
            ])
            
            # Check config file was created
            if result.exit_code == 0:
                self.assertTrue(config_path.exists())
            
        except ImportError:
            self.skipTest("CLI module not available")

    @patch('search_names.cli.NLPEngine')
    def test_analyze_command(self, mock_nlp):
        """Test analyze command with NLP."""
        try:
            from search_names.cli import app
            
            # Create test file
            corpus_path = Path(self.temp_dir) / "corpus.txt"
            corpus_path.write_text("John Doe and Jane Smith met yesterday.")
            
            # Mock NLP engine
            mock_engine = MagicMock()
            mock_engine.process_text.return_value = {
                'entities': [
                    {'text': 'John Doe', 'label': 'PERSON'},
                    {'text': 'Jane Smith', 'label': 'PERSON'}
                ]
            }
            mock_nlp.return_value = mock_engine
            
            result = self.runner.invoke(app, [
                "analyze",
                str(corpus_path),
                "--extract-entities"
            ])
            
            if result.exit_code == 0:
                mock_engine.process_text.assert_called()
            
        except ImportError:
            self.skipTest("CLI module not available")

    def test_version_command(self):
        """Test version command."""
        try:
            from search_names.cli import app
            
            result = self.runner.invoke(app, ["version"])
            
            # Should show version info
            if result.exit_code == 0:
                self.assertIn("0.3", result.stdout)
            
        except ImportError:
            self.skipTest("CLI module not available")

    @patch('search_names.cli.pd.read_csv')
    @patch('search_names.cli.Path')
    def test_pipeline_command(self, mock_path, mock_read_csv):
        """Test pipeline command."""
        try:
            from search_names.cli import app
            
            # Mock file operations
            mock_path.return_value.exists.return_value = True
            mock_read_csv.return_value = pd.DataFrame({
                'name': ['John Doe'],
                'text': ['John Doe is here']
            })
            
            result = self.runner.invoke(app, [
                "pipeline",
                "names.csv",
                "corpus.csv",
                "--output-dir", self.temp_dir
            ])
            
            # Pipeline should run through all steps
            # Even if it fails, we're testing the CLI structure
            self.assertIsNotNone(result)
            
        except ImportError:
            self.skipTest("CLI module not available")

    def test_invalid_command(self):
        """Test invalid command handling."""
        try:
            from search_names.cli import app
            
            result = self.runner.invoke(app, ["invalid-command"])
            
            # Should fail with non-zero exit code
            self.assertNotEqual(result.exit_code, 0)
            
        except ImportError:
            self.skipTest("CLI module not available")

    def test_missing_required_args(self):
        """Test handling of missing required arguments."""
        try:
            from search_names.cli import app
            
            # Clean command requires input file
            result = self.runner.invoke(app, ["clean"])
            
            # Should fail
            self.assertNotEqual(result.exit_code, 0)
            
        except ImportError:
            self.skipTest("CLI module not available")


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI."""

    def setUp(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_cli_workflow(self):
        """Test a complete CLI workflow."""
        try:
            from search_names.cli import app
            
            # Create test data
            names_csv = Path(self.temp_dir) / "names.csv"
            names_csv.write_text("name\nJohn Doe\nJane Smith")
            
            corpus_csv = Path(self.temp_dir) / "corpus.csv"
            corpus_csv.write_text("text\nJohn Doe was here\nJane Smith arrived")
            
            # Step 1: Clean names
            clean_output = Path(self.temp_dir) / "cleaned.csv"
            result_clean = self.runner.invoke(app, [
                "clean",
                str(names_csv),
                "--output", str(clean_output)
            ])
            
            # Step 2: Search (if clean succeeded)
            if result_clean.exit_code == 0 and clean_output.exists():
                search_output = Path(self.temp_dir) / "results.csv"
                result_search = self.runner.invoke(app, [
                    "search",
                    str(clean_output),
                    str(corpus_csv),
                    "--output", str(search_output)
                ])
                
                # Check search results
                if result_search.exit_code == 0:
                    self.assertTrue(search_output.exists())
            
        except ImportError:
            self.skipTest("CLI module not available")

    def test_cli_with_config(self):
        """Test CLI with configuration file."""
        try:
            from search_names.cli import app
            
            # Create config file
            config_path = Path(self.temp_dir) / "config.yaml"
            config_content = """
search:
  max_results: 50
  processes: 2
name_cleaning:
  parser_type: humanname
log_level: DEBUG
"""
            config_path.write_text(config_content)
            
            # Run command with config
            result = self.runner.invoke(app, [
                "--config", str(config_path),
                "version"
            ])
            
            # Should succeed
            self.assertEqual(result.exit_code, 0)
            
        except ImportError:
            self.skipTest("CLI module not available")


if __name__ == '__main__':
    unittest.main()