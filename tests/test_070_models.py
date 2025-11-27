#!/usr/bin/env python

"""
Tests for models module (Pydantic validation)
"""

import unittest

from pydantic import ValidationError

from search_names.models import (
    CleanedName,
    EntityMention,
    FileFormat,
    FuzzyMatchConfig,
    LogLevel,
    NameFormat,
    ProcessingStats,
    SearchJobConfig,
    SearchPattern,
    SearchRequest,
    SearchResponse,
    SearchResult,
    SupplementaryData,
    TextDocument,
)


class TestCleanedName(unittest.TestCase):
    """Test CleanedName model validation."""

    def test_valid_cleaned_name(self):
        """Test creating a valid CleanedName."""
        name = CleanedName(
            uniqid="001",
            first_name="John",
            last_name="Doe",
            original_name="Doe, John"
        )

        self.assertEqual(name.uniqid, "001")
        self.assertEqual(name.first_name, "John")
        self.assertEqual(name.last_name, "Doe")
        self.assertEqual(name.original_name, "Doe, John")

    def test_empty_uniqid_validation(self):
        """Test that empty uniqid raises validation error."""
        with self.assertRaises(ValidationError) as context:
            CleanedName(
                uniqid="",
                original_name="John Doe"
            )

        self.assertIn("uniqid cannot be empty", str(context.exception))

    def test_whitespace_only_uniqid(self):
        """Test that whitespace-only uniqid raises validation error."""
        with self.assertRaises(ValidationError):
            CleanedName(
                uniqid="   ",
                original_name="John Doe"
            )

    def test_empty_original_name_validation(self):
        """Test that empty original_name raises validation error."""
        with self.assertRaises(ValidationError) as context:
            CleanedName(
                uniqid="001",
                original_name=""
            )

        self.assertIn("original_name cannot be empty", str(context.exception))

    def test_optional_fields_none(self):
        """Test that optional fields can be None."""
        name = CleanedName(
            uniqid="001",
            original_name="John Doe",
            first_name=None,
            middle_name=None,
            last_name=None,
            prefix=None,
            suffix=None,
            roman_numeral=None
        )

        self.assertIsNone(name.first_name)
        self.assertIsNone(name.middle_name)


class TestSupplementaryData(unittest.TestCase):
    """Test SupplementaryData model validation."""

    def test_string_list_cleaning(self):
        """Test that string lists are properly cleaned."""
        data = SupplementaryData(
            prefixes="Mr.;Dr.;Prof.",
            nick_names="Bill;William;Will"
        )

        self.assertEqual(data.prefixes, "Mr.;Dr.;Prof.")
        self.assertEqual(data.nick_names, "Bill;William;Will")

    def test_list_to_string_conversion(self):
        """Test that lists are converted to semicolon-separated strings."""
        data = SupplementaryData(
            prefixes=["Mr.", "Dr.", "Prof."],
            nick_names=["Bill", "William", "Will"]
        )

        self.assertEqual(data.prefixes, "Mr.;Dr.;Prof.")
        self.assertEqual(data.nick_names, "Bill;William;Will")

    def test_none_values(self):
        """Test that None values are preserved."""
        data = SupplementaryData()

        self.assertIsNone(data.prefixes)
        self.assertIsNone(data.nick_names)
        self.assertIsNone(data.aliases)


class TestSearchPattern(unittest.TestCase):
    """Test SearchPattern model validation."""

    def test_valid_pattern(self):
        """Test creating a valid SearchPattern."""
        pattern = SearchPattern(
            pattern="FirstName LastName",
            uniqid="001",
            search_name="John Doe",
            confidence=0.95
        )

        self.assertEqual(pattern.pattern, "FirstName LastName")
        self.assertEqual(pattern.uniqid, "001")
        self.assertEqual(pattern.search_name, "John Doe")
        self.assertEqual(pattern.confidence, 0.95)

    def test_invalid_pattern_format(self):
        """Test that invalid pattern format raises validation error."""
        with self.assertRaises(ValidationError):
            SearchPattern(
                pattern="Invalid Pattern",
                uniqid="001",
                search_name="John Doe"
            )

    def test_confidence_bounds(self):
        """Test that confidence is bounded between 0 and 1."""
        # Valid confidence
        pattern = SearchPattern(
            pattern="FirstName LastName",
            uniqid="001",
            search_name="John Doe",
            confidence=0.5
        )
        self.assertEqual(pattern.confidence, 0.5)

        # Invalid confidence - too high
        with self.assertRaises(ValidationError):
            SearchPattern(
                pattern="FirstName LastName",
                uniqid="001",
                search_name="John Doe",
                confidence=1.5
            )

        # Invalid confidence - negative
        with self.assertRaises(ValidationError):
            SearchPattern(
                pattern="FirstName LastName",
                uniqid="001",
                search_name="John Doe",
                confidence=-0.1
            )


class TestSearchResult(unittest.TestCase):
    """Test SearchResult model validation."""

    def test_valid_search_result(self):
        """Test creating a valid SearchResult."""
        result = SearchResult(
            uniqid="001",
            match_count=2,
            matches=["John Doe", "J. Doe"],
            start_positions=[10, 50],
            end_positions=[18, 56],
            confidence_scores=[0.9, 0.8]
        )

        self.assertEqual(result.match_count, 2)
        self.assertEqual(len(result.matches), 2)
        self.assertEqual(len(result.start_positions), 2)
        self.assertEqual(len(result.end_positions), 2)
        self.assertEqual(len(result.confidence_scores), 2)

    def test_list_length_validation(self):
        """Test that all lists must have consistent lengths."""
        with self.assertRaises(ValidationError) as context:
            SearchResult(
                uniqid="001",
                match_count=2,
                matches=["John Doe", "J. Doe"],
                start_positions=[10],  # Wrong length
                end_positions=[18, 56]
            )

        self.assertIn("same length", str(context.exception))

    def test_match_count_validation(self):
        """Test that match_count must equal matches length."""
        with self.assertRaises(ValidationError) as context:
            SearchResult(
                uniqid="001",
                match_count=3,  # Doesn't match matches length
                matches=["John Doe", "J. Doe"],
                start_positions=[10, 50],
                end_positions=[18, 56]
            )

        self.assertIn("match_count must equal length of matches", str(context.exception))

    def test_empty_confidence_scores_allowed(self):
        """Test that empty confidence_scores list is allowed."""
        result = SearchResult(
            uniqid="001",
            match_count=1,
            matches=["John Doe"],
            start_positions=[10],
            end_positions=[18],
            confidence_scores=[]  # Empty is OK
        )

        self.assertEqual(len(result.confidence_scores), 0)


class TestTextDocument(unittest.TestCase):
    """Test TextDocument model validation."""

    def test_valid_document(self):
        """Test creating a valid TextDocument."""
        doc = TextDocument(
            uniqid="doc001",
            text="This is a sample document text.",
            metadata={"source": "test", "date": "2023-01-01"}
        )

        self.assertEqual(doc.uniqid, "doc001")
        self.assertEqual(doc.text, "This is a sample document text.")
        self.assertEqual(doc.metadata["source"], "test")

    def test_empty_text_validation(self):
        """Test that empty text raises validation error."""
        with self.assertRaises(ValidationError):
            TextDocument(
                uniqid="doc001",
                text=""
            )

    def test_whitespace_trimming(self):
        """Test that whitespace is trimmed from uniqid and text."""
        doc = TextDocument(
            uniqid="  doc001  ",
            text="  Sample text  "
        )

        self.assertEqual(doc.uniqid, "doc001")
        self.assertEqual(doc.text, "Sample text")


class TestSearchJobConfig(unittest.TestCase):
    """Test SearchJobConfig model validation."""

    def test_valid_job_config(self):
        """Test creating a valid SearchJobConfig."""
        config = SearchJobConfig(
            name_file="names.csv",
            text_file="corpus.csv",
            output_file="results.csv",
            max_results=50,
            processes=8,
            fuzzy_min_lengths=[[10, 1], [15, 2]]
        )

        self.assertEqual(config.max_results, 50)
        self.assertEqual(config.processes, 8)
        self.assertEqual(config.fuzzy_min_lengths, [[10, 1], [15, 2]])

    def test_positive_validation(self):
        """Test that numeric fields must be positive."""
        with self.assertRaises(ValidationError):
            SearchJobConfig(
                name_file="names.csv",
                text_file="corpus.csv",
                output_file="results.csv",
                max_results=0  # Must be >= 1
            )

    def test_fuzzy_lengths_validation(self):
        """Test fuzzy_min_lengths validation."""
        # Valid format
        config = SearchJobConfig(
            name_file="names.csv",
            text_file="corpus.csv",
            output_file="results.csv",
            fuzzy_min_lengths=[[10, 1], [15, 2]]
        )
        self.assertEqual(config.fuzzy_min_lengths, [[10, 1], [15, 2]])

        # Invalid format - wrong length
        with self.assertRaises(ValidationError):
            SearchJobConfig(
                name_file="names.csv",
                text_file="corpus.csv",
                output_file="results.csv",
                fuzzy_min_lengths=[(10,)]  # Should be length 2
            )

        # Invalid format - non-integers
        with self.assertRaises(ValidationError):
            SearchJobConfig(
                name_file="names.csv",
                text_file="corpus.csv",
                output_file="results.csv",
                fuzzy_min_lengths=[(10.5, 1)]  # Should be integers
            )


class TestFuzzyMatchConfig(unittest.TestCase):
    """Test FuzzyMatchConfig model validation."""

    def test_valid_fuzzy_config(self):
        """Test creating a valid FuzzyMatchConfig."""
        config = FuzzyMatchConfig(
            min_length=10,
            edit_distance=2
        )

        self.assertEqual(config.min_length, 10)
        self.assertEqual(config.edit_distance, 2)

    def test_edit_distance_validation(self):
        """Test edit distance validation against min_length."""
        # Valid - edit distance is reasonable
        config = FuzzyMatchConfig(
            min_length=10,
            edit_distance=3
        )
        self.assertEqual(config.edit_distance, 3)

        # Invalid - edit distance too large
        with self.assertRaises(ValidationError) as context:
            FuzzyMatchConfig(
                min_length=10,
                edit_distance=6  # More than half of min_length
            )

        self.assertIn("should not exceed half", str(context.exception))


class TestEntityMention(unittest.TestCase):
    """Test EntityMention model validation."""

    def test_valid_entity_mention(self):
        """Test creating a valid EntityMention."""
        mention = EntityMention(
            text="John Doe",
            label="PERSON",
            start=10,
            end=18,
            confidence=0.95
        )

        self.assertEqual(mention.text, "John Doe")
        self.assertEqual(mention.label, "PERSON")
        self.assertEqual(mention.start, 10)
        self.assertEqual(mention.end, 18)
        self.assertEqual(mention.confidence, 0.95)

    def test_position_validation(self):
        """Test that end position must be greater than start position."""
        with self.assertRaises(ValidationError) as context:
            EntityMention(
                text="John Doe",
                label="PERSON",
                start=18,
                end=10  # End before start
            )

        self.assertIn("end position must be greater than start", str(context.exception))

    def test_equal_positions_invalid(self):
        """Test that equal start and end positions are invalid."""
        with self.assertRaises(ValidationError):
            EntityMention(
                text="John Doe",
                label="PERSON",
                start=10,
                end=10  # Equal positions
            )


class TestProcessingStats(unittest.TestCase):
    """Test ProcessingStats model validation."""

    def test_derived_stats_calculation(self):
        """Test that derived statistics are calculated automatically."""
        stats = ProcessingStats(
            total_documents=1000,
            processed_documents=500,
            processing_time_seconds=100.0
        )

        # Should calculate documents_per_second automatically
        self.assertEqual(stats.documents_per_second, 5.0)

    def test_zero_time_handling(self):
        """Test handling of zero processing time."""
        stats = ProcessingStats(
            processed_documents=100,
            processing_time_seconds=0.0
        )

        # Should not divide by zero
        self.assertEqual(stats.documents_per_second, 0.0)


class TestEnums(unittest.TestCase):
    """Test enum validations."""

    def test_name_format_enum(self):
        """Test NameFormat enum values."""
        self.assertEqual(NameFormat.FIRST_LAST, "FirstName LastName")
        self.assertEqual(NameFormat.NICK_LAST, "NickName LastName")

    def test_file_format_enum(self):
        """Test FileFormat enum values."""
        self.assertEqual(FileFormat.CSV, "csv")
        self.assertEqual(FileFormat.JSON, "json")
        self.assertEqual(FileFormat.PARQUET, "parquet")

    def test_log_level_enum(self):
        """Test LogLevel enum values."""
        self.assertEqual(LogLevel.DEBUG, "DEBUG")
        self.assertEqual(LogLevel.INFO, "INFO")
        self.assertEqual(LogLevel.ERROR, "ERROR")


class TestComplexModels(unittest.TestCase):
    """Test complex models with nested validation."""

    def test_search_request_validation(self):
        """Test SearchRequest model validation."""
        documents = [
            TextDocument(uniqid="doc1", text="Sample text 1"),
            TextDocument(uniqid="doc2", text="Sample text 2")
        ]

        patterns = [
            SearchPattern(
                pattern="FirstName LastName",
                uniqid="001",
                search_name="John Doe"
            )
        ]

        request = SearchRequest(
            documents=documents,
            search_patterns=patterns
        )

        self.assertEqual(len(request.documents), 2)
        self.assertEqual(len(request.search_patterns), 1)

    def test_search_response_validation(self):
        """Test SearchResponse model validation."""
        results = [
            SearchResult(
                uniqid="001",
                match_count=1,
                matches=["John Doe"],
                start_positions=[10],
                end_positions=[18]
            )
        ]

        stats = ProcessingStats(
            total_documents=100,
            processed_documents=100,
            processing_time_seconds=50.0
        )

        response = SearchResponse(
            job_id="job123",
            results=results,
            stats=stats
        )

        self.assertEqual(response.job_id, "job123")
        self.assertEqual(len(response.results), 1)
        self.assertEqual(response.status, "completed")  # Default value


if __name__ == '__main__':
    unittest.main()
