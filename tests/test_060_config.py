#!/usr/bin/env python

"""
Tests for config module
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from search_names.config import (
    Config,
    ConfigManager,
    NameCleaningConfig,
    SearchConfig,
    create_sample_config,
    get_config,
    get_config_manager,
)


class TestConfigDataClasses(unittest.TestCase):
    """Test configuration dataclasses."""

    def test_search_config_defaults(self):
        """Test SearchConfig default values."""
        config = SearchConfig()

        self.assertEqual(config.max_results, 20)
        self.assertEqual(config.fuzzy_min_lengths, [(10, 1), (15, 2)])
        self.assertEqual(config.processes, 4)
        self.assertEqual(config.chunk_size, 1000)

    def test_name_cleaning_config_defaults(self):
        """Test NameCleaningConfig default values."""
        config = NameCleaningConfig()

        self.assertEqual(config.default_patterns, [
            "FirstName LastName",
            "NickName LastName",
            "Prefix LastName"
        ])
        self.assertTrue(config.drop_duplicates)

    def test_config_defaults(self):
        """Test main Config default values."""
        config = Config()

        self.assertIsInstance(config.search, SearchConfig)
        self.assertIsInstance(config.name_cleaning, NameCleaningConfig)
        self.assertEqual(config.log_level, "INFO")
        self.assertTrue(config.rich_tracebacks)


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.yaml"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_config_manager_no_file(self):
        """Test ConfigManager when no config file exists."""
        manager = ConfigManager(self.config_path)
        config = manager.load_config()

        self.assertIsInstance(config, Config)
        # Should load defaults when no file exists
        self.assertEqual(config.search.max_results, 20)

    def test_config_manager_with_yaml(self):
        """Test ConfigManager loading from YAML file."""
        # Create a test YAML file
        yaml_content = """
search:
  max_results: 50
  processes: 8

name_cleaning:
  drop_duplicates: false

log_level: DEBUG
"""
        with open(self.config_path, 'w') as f:
            f.write(yaml_content)

        manager = ConfigManager(self.config_path)
        config = manager.load_config()

        self.assertEqual(config.search.max_results, 50)
        self.assertEqual(config.search.processes, 8)
        self.assertFalse(config.name_cleaning.drop_duplicates)
        self.assertEqual(config.log_level, "DEBUG")

    def test_config_manager_save_load_roundtrip(self):
        """Test saving and loading configuration."""
        # Create a modified config
        config = Config()
        config.search.max_results = 100
        config.log_level = "WARNING"

        manager = ConfigManager(self.config_path)
        manager.save_config(config)

        # Load it back
        manager2 = ConfigManager(self.config_path)
        loaded_config = manager2.load_config()

        self.assertEqual(loaded_config.search.max_results, 100)
        self.assertEqual(loaded_config.log_level, "WARNING")

    def test_config_manager_invalid_yaml(self):
        """Test ConfigManager with invalid YAML file."""
        # Create invalid YAML
        with open(self.config_path, 'w') as f:
            f.write("invalid: yaml: content: [")

        manager = ConfigManager(self.config_path)
        # Should fall back to defaults without error
        config = manager.load_config()

        self.assertIsInstance(config, Config)
        self.assertEqual(config.search.max_results, 20)  # Default value

    @patch('search_names.config.Path.exists')
    def test_find_config_file_search_paths(self, mock_exists):
        """Test that ConfigManager searches standard config locations."""
        # Mock that the third path exists
        mock_exists.side_effect = lambda: False

        def exists_side_effect():
            # Return True only for the third call (second path)
            exists_side_effect.call_count += 1
            return exists_side_effect.call_count == 3
        exists_side_effect.call_count = 0
        mock_exists.side_effect = exists_side_effect

        manager = ConfigManager()
        # Should find the config file
        self.assertIsNotNone(manager.config_path)


class TestConfigGlobalFunctions(unittest.TestCase):
    """Test global configuration functions."""

    def setUp(self):
        # Reset the global config manager
        import search_names.config
        search_names.config._config_manager = None

    def test_get_config_default(self):
        """Test get_config returns default configuration."""
        config = get_config()

        self.assertIsInstance(config, Config)
        self.assertEqual(config.search.max_results, 20)

    @patch('search_names.config.ConfigManager')
    def test_get_config_manager_singleton(self, mock_config_manager):
        """Test that get_config_manager returns singleton."""
        mock_manager = MagicMock()
        mock_config_manager.return_value = mock_manager

        manager1 = get_config_manager()
        manager2 = get_config_manager()

        # Should be the same instance
        self.assertEqual(manager1, manager2)
        # ConfigManager should only be called once
        mock_config_manager.assert_called_once()

    def test_create_sample_config(self):
        """Test creating sample configuration file."""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            temp_path = f.name

        try:
            create_sample_config(temp_path)

            # Verify file was created
            self.assertTrue(Path(temp_path).exists())

            # Verify it's valid YAML
            with open(temp_path) as f:
                content = f.read()
                self.assertIn('search:', content)
                self.assertIn('max_results:', content)

        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestConfigValidation(unittest.TestCase):
    """Test configuration validation."""

    def test_nested_config_update(self):
        """Test that nested configuration updates work correctly."""
        config_dict = {
            'search': {
                'max_results': 100,
                'processes': 2
            },
            'log_level': 'DEBUG'
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config_dict, f)
            temp_path = f.name

        try:
            manager = ConfigManager(temp_path)
            config = manager.load_config()

            # Check that nested values were updated
            self.assertEqual(config.search.max_results, 100)
            self.assertEqual(config.search.processes, 2)
            # Check that other nested values kept defaults
            self.assertEqual(config.search.chunk_size, 1000)  # Should keep default

            # Check top-level value
            self.assertEqual(config.log_level, 'DEBUG')

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_config_serialization_completeness(self):
        """Test that all config fields are properly serialized."""
        config = Config()

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            temp_path = f.name

        try:
            manager = ConfigManager(temp_path)
            manager.save_config(config)

            # Load and verify all sections exist
            with open(temp_path) as f:
                import yaml
                saved_data = yaml.safe_load(f)

            required_sections = ['search', 'name_cleaning', 'text_processing', 'files', 'nlp']
            for section in required_sections:
                self.assertIn(section, saved_data)

        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
