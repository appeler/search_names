#!/usr/bin/env python

"""
Tests for enhanced_name_parser module
"""

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from search_names.enhanced_name_parser import (
    HAS_PARSERNAAM,
    NameParser,
    ParsedName,
    compare_parsers,
    parse_names,
)


class TestParsedName(unittest.TestCase):
    """Test ParsedName dataclass."""

    def test_parsed_name_creation(self):
        """Test creating a ParsedName object."""
        parsed = ParsedName(
            original="John Doe",
            first_name="John",
            last_name="Doe",
            confidence=0.95,
            parser_used="humanname",
        )

        self.assertEqual(parsed.original, "John Doe")
        self.assertEqual(parsed.first_name, "John")
        self.assertEqual(parsed.last_name, "Doe")
        self.assertEqual(parsed.confidence, 0.95)

    def test_full_name_method(self):
        """Test full_name method."""
        parsed = ParsedName(
            original="Dr. John M. Doe Jr.",
            title="Dr.",
            first_name="John",
            middle_name="M.",
            last_name="Doe",
            suffix="Jr.",
        )

        self.assertEqual(parsed.full_name(), "Dr. John M. Doe Jr.")

    def test_full_name_partial(self):
        """Test full_name with missing components."""
        parsed = ParsedName(original="John Doe", first_name="John", last_name="Doe")

        self.assertEqual(parsed.full_name(), "John Doe")

    def test_to_dict_method(self):
        """Test to_dict method."""
        parsed = ParsedName(
            original="John Doe", first_name="John", last_name="Doe", confidence=0.9
        )

        result = parsed.to_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["original"], "John Doe")
        self.assertEqual(result["first_name"], "John")
        self.assertEqual(result["last_name"], "Doe")
        self.assertEqual(result["confidence"], 0.9)
        self.assertEqual(result["parser_used"], "humanname")


class TestNameParser(unittest.TestCase):
    """Test NameParser class."""

    def test_name_parser_init_default(self):
        """Test NameParser initialization with defaults."""
        parser = NameParser()

        self.assertEqual(parser.parser_type, "auto")
        self.assertEqual(parser.batch_size, 100)
        self.assertEqual(parser.ml_threshold, 0.8)

    @patch("search_names.enhanced_name_parser.HAS_PARSERNAAM", False)
    def test_name_parser_fallback_to_humanname(self):
        """Test fallback when parsernaam not available."""
        parser = NameParser(parser_type="parsernaam")

        # Should fall back to humanname
        self.assertEqual(parser.parser_type, "humanname")

    @patch("search_names.enhanced_name_parser.HumanName")
    def test_parse_with_humanname(self, mock_humanname):
        """Test parsing with HumanName."""
        mock_parsed = MagicMock()
        mock_parsed.first = "John"
        mock_parsed.middle = "M"
        mock_parsed.last = "Doe"
        mock_parsed.title = "Dr"
        mock_parsed.suffix = "Jr"
        mock_parsed.nickname = None
        mock_humanname.return_value = mock_parsed

        parser = NameParser(parser_type="humanname")
        result = parser.parse_with_humanname("Dr John M Doe Jr")

        self.assertIsInstance(result, ParsedName)
        self.assertEqual(result.first_name, "John")
        self.assertEqual(result.middle_name, "M")
        self.assertEqual(result.last_name, "Doe")
        self.assertEqual(result.title, "Dr")
        self.assertEqual(result.suffix, "Jr")
        self.assertEqual(result.parser_used, "humanname")

    @patch("search_names.enhanced_name_parser.HumanName")
    def test_parse_with_humanname_error(self, mock_humanname):
        """Test error handling in humanname parsing."""
        mock_humanname.side_effect = Exception("Parse error")

        parser = NameParser()
        result = parser.parse_with_humanname("Invalid Name")

        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(result.parser_used, "humanname")

    @patch("search_names.enhanced_name_parser.HAS_PARSERNAAM", True)
    @patch("search_names.enhanced_name_parser.ParseNames")
    def test_parse_with_parsernaam(self, mock_parsenames):
        """Test parsing with parsernaam."""
        # Mock parsernaam output
        mock_result = pd.DataFrame(
            {"first_name": ["John"], "last_name": ["Doe"], "confidence": [0.85]}
        )
        mock_parsenames.parse.return_value = mock_result

        parser = NameParser(parser_type="parsernaam")
        results = parser.parse_with_parsernaam(["John Doe"])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].parser_used, "parsernaam")

    @patch("search_names.enhanced_name_parser.HAS_PARSERNAAM", False)
    def test_parse_with_parsernaam_unavailable(self):
        """Test parsernaam fallback when not available."""
        parser = NameParser()
        results = parser.parse_with_parsernaam(["John Doe"])

        # Should fall back to humanname
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].parser_used, "humanname")

    def test_is_indian_name(self):
        """Test Indian name detection."""
        parser = NameParser()

        # Test Indian names
        self.assertTrue(parser.is_indian_name("Rajesh Kumar"))
        self.assertTrue(parser.is_indian_name("Priya Sharma"))
        self.assertTrue(parser.is_indian_name("Venkat Reddy"))
        self.assertTrue(parser.is_indian_name("Anita Patel"))

        # Test non-Indian names
        self.assertFalse(parser.is_indian_name("John Smith"))
        self.assertFalse(parser.is_indian_name("Jane Doe"))
        self.assertFalse(parser.is_indian_name("Robert Johnson"))

    def test_parse_single_name(self):
        """Test parsing a single name."""
        parser = NameParser(parser_type="humanname")
        result = parser.parse("John Doe")

        self.assertIsInstance(result, ParsedName)
        self.assertEqual(result.original, "John Doe")

    def test_parse_list_of_names(self):
        """Test parsing a list of names."""
        parser = NameParser(parser_type="humanname")
        names = ["John Doe", "Jane Smith"]
        results = parser.parse(names)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], ParsedName)
        self.assertIsInstance(results[1], ParsedName)

    @patch("search_names.enhanced_name_parser.HAS_PARSERNAAM", True)
    @patch("search_names.enhanced_name_parser.ParseNames")
    def test_parse_auto_mode(self, mock_parsenames):
        """Test auto mode with mixed names."""
        # Mock parsernaam for Indian names
        mock_result = pd.DataFrame(
            {"first_name": ["Rajesh"], "last_name": ["Kumar"], "confidence": [0.9]}
        )
        mock_parsenames.parse.return_value = mock_result

        parser = NameParser(parser_type="auto")

        # Test with mixed names
        names = ["John Smith", "Rajesh Kumar", "Jane Doe"]
        results = parser.parse(names)

        self.assertEqual(len(results), 3)
        # John Smith should use humanname
        self.assertEqual(results[0].parser_used, "humanname")
        # Rajesh Kumar should use parsernaam (if available)
        if HAS_PARSERNAAM:
            self.assertEqual(results[1].parser_used, "parsernaam")
        # Jane Doe should use humanname
        self.assertEqual(results[2].parser_used, "humanname")

    def test_parse_dataframe(self):
        """Test parsing names in a DataFrame."""
        df = pd.DataFrame({"name": ["John Doe", "Jane Smith"], "id": [1, 2]})

        parser = NameParser(parser_type="humanname")
        result_df = parser.parse_dataframe(df, name_column="name")

        # Check new columns were added
        self.assertIn("parsed_first_name", result_df.columns)
        self.assertIn("parsed_last_name", result_df.columns)
        self.assertIn("parsed_confidence", result_df.columns)
        self.assertIn("parser_used", result_df.columns)

        # Check data integrity
        self.assertEqual(len(result_df), 2)

    def test_parse_dataframe_invalid_column(self):
        """Test error handling for invalid column."""
        df = pd.DataFrame({"id": [1, 2]})

        parser = NameParser()
        with self.assertRaises(ValueError) as context:
            parser.parse_dataframe(df, name_column="invalid")

        self.assertIn("Column 'invalid' not found", str(context.exception))

    def test_parse_dataframe_no_components(self):
        """Test DataFrame parsing without adding components."""
        df = pd.DataFrame({"name": ["John Doe"], "id": [1]})

        parser = NameParser()
        result_df = parser.parse_dataframe(df, add_components=False)

        # Should add parsed_name column instead
        self.assertIn("parsed_name", result_df.columns)
        self.assertNotIn("parsed_first_name", result_df.columns)

        # Check that parsed_name contains ParsedName objects
        self.assertIsInstance(result_df["parsed_name"].iloc[0], ParsedName)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    def test_parse_names_single(self):
        """Test parse_names with single name."""
        result = parse_names("John Doe")

        self.assertIsInstance(result, ParsedName)
        self.assertEqual(result.original, "John Doe")

    def test_parse_names_list(self):
        """Test parse_names with list."""
        results = parse_names(["John Doe", "Jane Smith"])

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

    def test_parse_names_dataframe(self):
        """Test parse_names with DataFrame."""
        df = pd.DataFrame({"name": ["John Doe"]})
        result_df = parse_names(df)

        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertIn("parsed_first_name", result_df.columns)

    @patch("search_names.enhanced_name_parser.HAS_PARSERNAAM", True)
    @patch("search_names.enhanced_name_parser.NameParser")
    def test_compare_parsers(self, mock_parser_class):
        """Test compare_parsers function."""
        # Mock different parser results
        mock_hn_result = ParsedName(
            original="John Doe",
            first_name="John",
            last_name="Doe",
            parser_used="humanname",
        )

        mock_pn_result = ParsedName(
            original="John Doe",
            first_name="John",
            last_name="Doe",
            confidence=0.85,
            parser_used="parsernaam",
        )

        mock_auto_result = ParsedName(
            original="John Doe", first_name="John", last_name="Doe", parser_used="auto"
        )

        # Setup mock instances
        mock_instances = {
            "humanname": MagicMock(parse=MagicMock(return_value=mock_hn_result)),
            "parsernaam": MagicMock(parse=MagicMock(return_value=mock_pn_result)),
            "auto": MagicMock(parse=MagicMock(return_value=mock_auto_result)),
        }

        def get_mock_instance(parser_type=None):
            return mock_instances.get(parser_type, mock_instances["auto"])

        mock_parser_class.side_effect = get_mock_instance

        results = compare_parsers("John Doe")

        self.assertIn("humanname", results)
        self.assertIn("auto", results)
        if HAS_PARSERNAAM:
            self.assertIn("parsernaam", results)

    @patch("search_names.enhanced_name_parser.HAS_PARSERNAAM", False)
    def test_compare_parsers_no_parsernaam(self):
        """Test compare_parsers when parsernaam not available."""
        results = compare_parsers("John Doe")

        self.assertIn("humanname", results)
        self.assertIn("auto", results)
        self.assertNotIn("parsernaam", results)


class TestIntegration(unittest.TestCase):
    """Integration tests for name parsing."""

    def test_full_parsing_pipeline(self):
        """Test full parsing pipeline with various names."""
        names = [
            "John Doe",
            "Dr. Jane Smith Jr.",
            "Robert James Johnson III",
            "Mary-Jane O'Connor",
        ]

        parser = NameParser(parser_type="humanname")
        results = parser.parse(names)

        self.assertEqual(len(results), len(names))

        # Check each result
        for result, original in zip(results, names, strict=False):
            self.assertEqual(result.original, original)
            self.assertIsNotNone(result.first_name or result.last_name)
            self.assertEqual(result.parser_used, "humanname")

    def test_dataframe_integration(self):
        """Test DataFrame integration."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["John Doe", "Jane Smith", "Bob Johnson"],
                "age": [30, 25, 35],
            }
        )

        # Parse names
        result_df = parse_names(df, parser_type="humanname")

        # Verify structure
        self.assertEqual(len(result_df), 3)
        self.assertIn("parsed_first_name", result_df.columns)
        self.assertIn("parsed_last_name", result_df.columns)

        # Verify parsing
        self.assertIsNotNone(result_df["parsed_first_name"].iloc[0])
        self.assertIsNotNone(result_df["parsed_last_name"].iloc[0])

    def test_error_recovery(self):
        """Test error recovery in parsing."""
        # Include some problematic names
        names = [
            "John Doe",
            "",  # Empty name
            "   ",  # Whitespace only
            "A",  # Single letter
            "Jane Smith",
        ]

        parser = NameParser()
        results = parser.parse(names)

        # Should handle all names without crashing
        self.assertEqual(len(results), len(names))

        # Check that valid names were parsed
        self.assertIsNotNone(results[0].first_name)
        self.assertIsNotNone(results[4].first_name)


if __name__ == "__main__":
    unittest.main()
