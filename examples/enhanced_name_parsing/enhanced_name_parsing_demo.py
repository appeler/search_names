#!/usr/bin/env python3
"""
Enhanced Name Parsing Demo

This example demonstrates the enhanced name parsing capabilities of the search_names package,
including dual parser support (HumanName + parsernaam), confidence scoring, and intelligent
parser selection.

Key Features Demonstrated:
- Enhanced name parser with dual backend support
- Automatic Indian name detection for ML parser selection
- Confidence scoring and parser comparison
- Batch processing with pandas DataFrame integration
- Error handling and graceful degradation
"""

from pathlib import Path

import pandas as pd

# Import the enhanced name parsing functionality
from search_names.enhanced_name_parser import NameParser, compare_parsers
from search_names.logging_config import get_logger, setup_logging

# Set up logging
setup_logging()
logger = get_logger("enhanced_name_parsing_demo")


def demo_basic_parsing():
    """Demonstrate basic enhanced name parsing."""
    print("\n" + "=" * 60)
    print("BASIC ENHANCED NAME PARSING")
    print("=" * 60)

    # Sample names including some that might benefit from ML parsing
    sample_names = [
        "HALL, GUS",
        "BROWN, EDMUND G JR",
        "SHRIVER, ROBERT SARGENT, JR.",
        "UDALL, MORRIS K.",
        "LAROUCHE, LYNDON H.",
        "Rajesh Kumar Sharma",  # Indian name that benefits from ML parsing
        "Priya Devi Gupta",  # Another Indian name
        "Dr. Sarah Johnson-Smith",  # Complex Western name
    ]

    # Create parser with auto-selection
    parser = NameParser(parser_type="auto")

    print("Parsing names with intelligent parser selection:")
    print("-" * 50)

    for name in sample_names:
        result = parser.parse(name)

        print(f"Original: {result.original}")
        print(f"  First: {result.first_name}")
        print(f"  Middle: {result.middle_name}")
        print(f"  Last: {result.last_name}")
        print(f"  Title: {result.title}")
        print(f"  Suffix: {result.suffix}")
        print(f"  Parser Used: {result.parser_used}")
        print(f"  Confidence: {result.confidence:.2f}")
        print()


def demo_parser_comparison():
    """Demonstrate comparison between different parsers."""
    print("\n" + "=" * 60)
    print("PARSER COMPARISON")
    print("=" * 60)

    # Names that might be parsed differently by different parsers
    test_names = [
        "Rajesh Kumar Sharma",
        "BROWN, EDMUND G JR",
        "Dr. Priya Devi",
        "SHRIVER, ROBERT SARGENT, JR.",
    ]

    print("Comparing parsers on sample names:")
    print("-" * 50)

    for name in test_names:
        print(f"\nParsing: '{name}'")
        results = compare_parsers(name)

        for parser_name, result in results.items():
            print(
                f"  {parser_name:12}: {result.first_name} | {result.middle_name} | {result.last_name} "
                f"| confidence: {result.confidence:.2f}"
            )


def demo_dataframe_processing():
    """Demonstrate DataFrame integration with enhanced parsing."""
    print("\n" + "=" * 60)
    print("DATAFRAME PROCESSING")
    print("=" * 60)

    # Create sample data similar to the political candidate data
    data = {
        "Name": [
            "HALL, GUS",
            "BROWN, EDMUND G JR",
            "SHRIVER, ROBERT SARGENT, JR.",
            "Rajesh Kumar Singh",
            "Priya Sharma Devi",
            "UDALL, MORRIS K.",
            "Dr. Sarah Johnson-Smith",
            "Mohammad Abdul Rahman",
        ],
        "Party": [328, 100, 100, 100, 100, 100, 200, 200],
        "State": [0, 0, 0, 5, 5, 0, 10, 15],
    }

    df = pd.DataFrame(data)
    print("Original DataFrame:")
    print(df.to_string(index=False))

    # Parse names using the enhanced parser
    parser = NameParser(parser_type="auto")
    enhanced_df = parser.parse_dataframe(df, name_column="Name")

    print("\nEnhanced DataFrame with parsed components:")
    print("-" * 50)

    # Display relevant columns
    display_cols = [
        "Name",
        "parsed_first_name",
        "parsed_last_name",
        "parsed_confidence",
        "parser_used",
    ]
    print(enhanced_df[display_cols].to_string(index=False))

    return enhanced_df


def demo_batch_processing():
    """Demonstrate efficient batch processing."""
    print("\n" + "=" * 60)
    print("BATCH PROCESSING EFFICIENCY")
    print("=" * 60)

    # Create larger dataset for batch processing demo
    names = [
        "Smith, John",
        "Johnson, Mary Elizabeth",
        "Rajesh Kumar Patel",
        "Dr. Sarah Wilson-Brown",
        "Priya Sharma Gupta",
        "Mohammad Abdul Hassan",
        "Chen, Wei-Ming",
        "Garcia, Maria Santos",
    ] * 10  # Repeat to create larger dataset

    print(f"Processing {len(names)} names in batch...")

    # Test different parser configurations
    configs = [
        ("HumanName Only", "humanname"),
        ("Auto Selection", "auto"),
        ("parsernaam (if available)", "parsernaam"),
    ]

    for config_name, parser_type in configs:
        try:
            parser = NameParser(parser_type=parser_type)
            results = parser.parse(names)

            # Calculate statistics
            confidence_scores = [r.confidence for r in results]
            avg_confidence = sum(confidence_scores) / len(confidence_scores)

            parser_counts = {}
            for r in results:
                parser_counts[r.parser_used] = parser_counts.get(r.parser_used, 0) + 1

            print(f"\n{config_name}:")
            print(f"  Average Confidence: {avg_confidence:.3f}")
            print(f"  Parser Usage: {dict(parser_counts)}")

        except Exception as e:
            print(f"\n{config_name}: Error - {e}")


def demo_error_handling():
    """Demonstrate robust error handling."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING & EDGE CASES")
    print("=" * 60)

    # Edge cases and problematic names
    edge_cases = [
        "",  # Empty string
        "   ",  # Whitespace only
        "X",  # Single character
        "123",  # Numbers only
        "Mr. Dr. Prof. John Smith PhD Jr.",  # Multiple titles/suffixes
        "Jean-Claude Van Damme",  # Hyphens
        "Mary O'Connor",  # Apostrophes
        "José María García",  # Unicode characters
    ]

    parser = NameParser(parser_type="auto")

    print("Testing edge cases and error handling:")
    print("-" * 50)

    for name in edge_cases:
        try:
            result = parser.parse(name)
            print(
                f"'{name}' -> "
                f"First: '{result.first_name}', "
                f"Last: '{result.last_name}', "
                f"Confidence: {result.confidence:.2f}"
            )
        except Exception as e:
            print(f"'{name}' -> ERROR: {e}")


def demo_configuration_options():
    """Demonstrate configuration options."""
    print("\n" + "=" * 60)
    print("CONFIGURATION OPTIONS")
    print("=" * 60)

    test_name = "Rajesh Kumar Singh"

    # Test different configurations
    configs = [
        ("Default", {}),
        ("High ML Threshold", {"ml_threshold": 0.95}),
        ("Large Batch Size", {"batch_size": 500}),
        ("Force HumanName", {"parser_type": "humanname"}),
    ]

    print("Testing different configurations:")
    print("-" * 50)

    for config_name, kwargs in configs:
        try:
            parser = NameParser(**kwargs)
            result = parser.parse(test_name)

            print(
                f"{config_name:20}: "
                f"Parser: {result.parser_used:10}, "
                f"Confidence: {result.confidence:.3f}"
            )
        except Exception as e:
            print(f"{config_name:20}: ERROR - {e}")


def save_example_output(df):
    """Save example output to demonstrate different formats."""
    print("\n" + "=" * 60)
    print("SAVING ENHANCED RESULTS")
    print("=" * 60)

    output_dir = Path("enhanced_name_parsing")
    output_dir.mkdir(exist_ok=True)

    # Save in different formats
    formats = [
        ("CSV", "enhanced_names.csv", df.to_csv),
        (
            "JSON",
            "enhanced_names.json",
            lambda f: df.to_json(f, orient="records", indent=2),
        ),
    ]

    # Try Parquet if available
    try:
        import pyarrow  # noqa: F401

        formats.append(("Parquet", "enhanced_names.parquet", df.to_parquet))
    except ImportError:
        print("Parquet format not available (install pyarrow for Parquet support)")

    for format_name, filename, save_func in formats:
        try:
            filepath = output_dir / filename
            save_func(filepath)
            print(f"Saved {format_name}: {filepath}")
        except Exception as e:
            print(f"Error saving {format_name}: {e}")


def main():
    """Run all demonstrations."""
    print("Enhanced Name Parsing Demo")
    print("=" * 80)
    print("This demo showcases the enhanced name parsing capabilities")
    print("of the modernized search_names package.")

    # Run all demonstrations
    demo_basic_parsing()
    demo_parser_comparison()
    df = demo_dataframe_processing()
    demo_batch_processing()
    demo_error_handling()
    demo_configuration_options()
    save_example_output(df)

    print("\n" + "=" * 80)
    print("Demo completed! Check the output files for saved results.")
    print("\nKey improvements over legacy approach:")
    print("- Dual parser support (HumanName + parsernaam)")
    print("- Intelligent auto-selection based on name patterns")
    print("- Confidence scoring for all results")
    print("- Robust error handling and graceful degradation")
    print("- Modern pandas DataFrame integration")
    print("- Multiple output format support")
    print("=" * 80)


if __name__ == "__main__":
    main()
