#!/usr/bin/env python3
"""
Complete Workflow Demo

This example demonstrates end-to-end workflows using the modernized search_names package,
showing how all components work together in real-world scenarios.
"""

from pathlib import Path

import pandas as pd

from search_names.config import NameCleaningConfig
from search_names.enhanced_name_parser import NameParser
from search_names.logging_config import get_logger, setup_logging

# Set up logging
setup_logging()
logger = get_logger("workflow_demo")


def demo_complete_name_processing_workflow():
    """Demonstrate a complete name processing workflow."""
    print("=" * 80)
    print("COMPLETE NAME PROCESSING WORKFLOW")
    print("=" * 80)

    # Create sample political dataset
    sample_data = {
        "candidate_id": ["C001", "C002", "C003", "C004", "C005"],
        "raw_name": [
            "BIDEN, JOSEPH R JR",
            "Warren, Elizabeth Ann",
            "Rajesh Kumar Patel",
            "Dr. Sarah Johnson-Smith, PhD",
            "Mohammad Abdul Rahman",
        ],
        "party": ["DEM", "DEM", "IND", "REP", "DEM"],
        "state": ["DE", "MA", "CA", "TX", "MI"],
        "office": ["President", "Senator", "Representative", "Governor", "Mayor"],
    }

    df = pd.DataFrame(sample_data)
    print("Input Dataset:")
    print(df.to_string(index=False))
    print()

    # Configure enhanced name parser
    config = NameCleaningConfig(
        parser_type="auto",  # Intelligent parser selection
        batch_size=100,
        ml_threshold=0.8,
    )

    parser = NameParser(
        parser_type=config.parser_type,
        batch_size=config.batch_size,
        ml_threshold=config.ml_threshold,
    )

    # Process names with enhanced parsing
    print("Processing names with enhanced parser...")
    enhanced_df = parser.parse_dataframe(df, name_column="raw_name")

    # Display results
    print("\nProcessed Results:")
    result_cols = [
        "candidate_id",
        "raw_name",
        "parsed_first_name",
        "parsed_last_name",
        "parsed_confidence",
        "parser_used",
    ]
    print(enhanced_df[result_cols].to_string(index=False))

    # Statistics
    stats = {
        "total_processed": len(enhanced_df),
        "avg_confidence": enhanced_df["parsed_confidence"].mean(),
        "high_confidence": (enhanced_df["parsed_confidence"] >= 0.8).sum(),
        "parser_usage": enhanced_df["parser_used"].value_counts().to_dict(),
    }

    print("\nProcessing Statistics:")
    print(f"  Total processed: {stats['total_processed']}")
    print(f"  Average confidence: {stats['avg_confidence']:.3f}")
    print(f"  High confidence (≥0.8): {stats['high_confidence']}")
    print(f"  Parser usage: {stats['parser_usage']}")

    return enhanced_df


def demo_multi_format_export():
    """Demonstrate exporting to multiple formats."""
    print("\n" + "=" * 80)
    print("MULTI-FORMAT DATA EXPORT")
    print("=" * 80)

    # Generate some data
    parser = NameParser(parser_type="auto")
    names = ["John Smith", "Priya Sharma", "Chen Wei-Ming", "Maria Santos"]
    results = parser.parse(names)

    # Convert to DataFrame
    df_data = []
    for result in results:
        df_data.append(
            {
                "original_name": result.original,
                "first_name": result.first_name,
                "middle_name": result.middle_name,
                "last_name": result.last_name,
                "confidence": result.confidence,
                "parser_used": result.parser_used,
            }
        )

    df = pd.DataFrame(df_data)

    # Export to different formats
    output_dir = Path("integration_workflows")
    output_dir.mkdir(exist_ok=True)

    formats = [
        ("CSV", "processed_names.csv", lambda f: df.to_csv(f, index=False)),
        (
            "JSON",
            "processed_names.json",
            lambda f: df.to_json(f, orient="records", indent=2),
        ),
    ]

    # Try Parquet if available
    try:
        import pyarrow  # noqa: F401

        formats.append(
            (
                "Parquet",
                "processed_names.parquet",
                lambda f: df.to_parquet(f, index=False),
            )
        )
    except ImportError:
        print("Parquet format not available (pyarrow not installed)")

    print("Exporting processed data to multiple formats:")
    for format_name, filename, save_func in formats:
        try:
            filepath = output_dir / filename
            save_func(filepath)
            file_size = filepath.stat().st_size
            print(f"  ✓ {format_name}: {filename} ({file_size} bytes)")
        except Exception as e:
            print(f"  ✗ {format_name}: Failed - {e}")


def demo_batch_processing_workflow():
    """Demonstrate efficient batch processing."""
    print("\n" + "=" * 80)
    print("BATCH PROCESSING WORKFLOW")
    print("=" * 80)

    # Create larger dataset for batch processing
    base_names = [
        "Smith, John",
        "Johnson, Mary Elizabeth",
        "Rajesh Kumar Patel",
        "Chen, Wei-Ming",
        "Garcia, Maria Santos",
        "Dr. Sarah Wilson",
        "Mohammad Abdul Hassan",
        "Priya Sharma Gupta",
    ]

    # Replicate to create larger dataset
    large_dataset = base_names * 25  # 200 names

    print(f"Processing {len(large_dataset)} names in batch...")

    # Time the processing
    import time

    # Test different batch sizes
    batch_sizes = [50, 100, 200]

    for batch_size in batch_sizes:
        start_time = time.time()

        parser = NameParser(parser_type="auto", batch_size=batch_size)
        results = parser.parse(large_dataset)

        end_time = time.time()
        processing_time = end_time - start_time

        # Calculate statistics
        confidence_scores = [r.confidence for r in results]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)

        print(f"\nBatch size {batch_size}:")
        print(f"  Processing time: {processing_time:.2f}s")
        print(f"  Names per second: {len(large_dataset) / processing_time:.1f}")
        print(f"  Average confidence: {avg_confidence:.3f}")


def demo_error_handling_workflow():
    """Demonstrate robust error handling in workflows."""
    print("\n" + "=" * 80)
    print("ERROR HANDLING WORKFLOW")
    print("=" * 80)

    # Create dataset with problematic entries
    problematic_data = {
        "id": ["P001", "P002", "P003", "P004", "P005"],
        "name": [
            "",  # Empty name
            "   ",  # Whitespace only
            "Valid Name",  # Good name
            "12345",  # Numbers only
            "José María García-López",  # Unicode characters
        ],
        "category": ["empty", "whitespace", "valid", "numeric", "unicode"],
    }

    df = pd.DataFrame(problematic_data)
    print("Dataset with problematic entries:")
    print(df.to_string(index=False))
    print()

    # Process with error handling
    parser = NameParser(parser_type="auto")

    processed_results = []
    errors = []

    for _idx, row in df.iterrows():
        try:
            result = parser.parse(row["name"])
            processed_results.append(
                {
                    "id": row["id"],
                    "category": row["category"],
                    "original": result.original,
                    "first_name": result.first_name,
                    "last_name": result.last_name,
                    "confidence": result.confidence,
                    "status": "success",
                }
            )
        except Exception as e:
            errors.append(
                {
                    "id": row["id"],
                    "category": row["category"],
                    "original": row["name"],
                    "error": str(e),
                    "status": "error",
                }
            )

    print("Processing Results:")
    results_df = pd.DataFrame(processed_results)
    if not results_df.empty:
        print(results_df.to_string(index=False))

    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors:
            print(f"  ID {error['id']} ({error['category']}): {error['error']}")
    else:
        print("\nNo errors encountered!")


def demo_configuration_workflow():
    """Demonstrate configuration-driven workflows."""
    print("\n" + "=" * 80)
    print("CONFIGURATION-DRIVEN WORKFLOW")
    print("=" * 80)

    # Different configurations for different use cases
    configs = [
        ("High Accuracy", {"parser_type": "humanname", "ml_threshold": 0.95}),
        ("Balanced", {"parser_type": "auto", "ml_threshold": 0.8}),
        ("ML Optimized", {"parser_type": "parsernaam", "ml_threshold": 0.7}),
    ]

    test_names = ["Rajesh Kumar Singh", "Dr. Elizabeth Warren", "BIDEN, JOSEPH R JR"]

    print("Testing different configurations:")

    for config_name, config_params in configs:
        print(f"\n{config_name} Configuration:")
        try:
            parser = NameParser(**config_params)

            for name in test_names:
                result = parser.parse(name)
                print(
                    f"  '{name}' -> {result.first_name} {result.last_name} "
                    f"(confidence: {result.confidence:.3f}, parser: {result.parser_used})"
                )

        except Exception as e:
            print(f"  Error with {config_name} config: {e}")


def main():
    """Run all workflow demonstrations."""
    print("Complete Integration Workflows Demo")
    print("=" * 80)
    print("This demo shows end-to-end workflows using all package features.")

    # Run workflow demonstrations
    demo_complete_name_processing_workflow()
    demo_multi_format_export()
    demo_batch_processing_workflow()
    demo_error_handling_workflow()
    demo_configuration_workflow()

    print("\n" + "=" * 80)
    print("Integration Workflows Demo Completed!")
    print("\nKey workflow capabilities demonstrated:")
    print("- Complete name processing pipeline")
    print("- Multi-format data export (CSV, JSON, Parquet)")
    print("- Efficient batch processing with performance metrics")
    print("- Robust error handling and validation")
    print("- Configuration-driven processing")
    print("- Type-safe DataFrame integration")
    print("=" * 80)


if __name__ == "__main__":
    main()
