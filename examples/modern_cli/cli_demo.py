#!/usr/bin/env python3
"""
Modern CLI Demo

This example demonstrates the modernized CLI interface using typer instead of the legacy argparse.
Shows configuration management, multiple output formats, and enhanced name parsing capabilities.

Key Features:
- Modern typer-based CLI with rich help messages
- YAML configuration file support
- Multiple output formats (CSV, JSON, Parquet)
- Enhanced name parsing with confidence scoring
- Progress indicators and rich logging
- Type hints and validation
"""

from pathlib import Path

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from search_names.config import NameCleaningConfig, load_config
from search_names.enhanced_name_parser import NameParser
from search_names.logging_config import get_logger, setup_logging

# Set up console and logging
console = Console()
setup_logging()
logger = get_logger("cli_demo")

# Create the typer app
app = typer.Typer(
    name="name-processor",
    help="Modern name processing CLI with enhanced parsing capabilities",
    rich_markup_mode="rich"
)


@app.command()
def process_names(
    input_file: Path = typer.Argument(..., help="Input CSV file containing names"),
    output_file: Path | None = typer.Option(None, "-o", "--output", help="Output file (auto-detects format from extension)"),
    name_column: str = typer.Option("Name", "-c", "--column", help="Column containing names to process"),
    parser_type: str = typer.Option("auto", "-p", "--parser", help="Parser type: humanname, parsernaam, or auto"),
    config_file: Path | None = typer.Option(None, "--config", help="YAML configuration file"),
    format: str = typer.Option("csv", "-f", "--format", help="Output format: csv, json, parquet"),
    show_confidence: bool = typer.Option(True, "--confidence/--no-confidence", help="Include confidence scores"),
    show_progress: bool = typer.Option(True, "--progress/--no-progress", help="Show progress bar"),
    batch_size: int = typer.Option(100, "--batch-size", help="Batch size for processing"),
    ml_threshold: float = typer.Option(0.8, "--ml-threshold", help="ML confidence threshold"),
):
    """
    Process names in a CSV file with enhanced parsing capabilities.

    [bold green]Examples:[/bold green]

    [dim]# Basic processing with auto parser selection[/dim]
    python cli_demo.py process-names input.csv -o output.csv

    [dim]# Use specific parser with JSON output[/dim]
    python cli_demo.py process-names input.csv -p parsernaam -f json -o output.json

    [dim]# Use configuration file[/dim]
    python cli_demo.py process-names input.csv --config config.yaml -o output.parquet
    """
    console.print(f"[bold blue]Processing names from {input_file}[/bold blue]")

    # Load configuration if provided
    if config_file and config_file.exists():
        config = load_config(config_file)
        console.print(f"[green]Loaded configuration from {config_file}[/green]")
    else:
        config = NameCleaningConfig(
            parser_type=parser_type,
            batch_size=batch_size,
            ml_threshold=ml_threshold
        )

    # Validate input file
    if not input_file.exists():
        console.print(f"[red]Error: Input file {input_file} does not exist[/red]")
        raise typer.Exit(1)

    try:
        # Load input data
        console.print(f"[dim]Loading data from {input_file}...[/dim]")
        df = pd.read_csv(input_file)

        if name_column not in df.columns:
            console.print(f"[red]Error: Column '{name_column}' not found in input file[/red]")
            console.print(f"Available columns: {', '.join(df.columns)}")
            raise typer.Exit(1)

        console.print(f"[green]Loaded {len(df)} records[/green]")

        # Initialize parser
        parser = NameParser(
            parser_type=config.parser_type,
            batch_size=config.batch_size,
            ml_threshold=config.ml_threshold
        )

        console.print(f"[blue]Using parser: {config.parser_type}[/blue]")

        # Process names with progress bar
        if show_progress:
            console.print("[dim]Processing names...[/dim]")

        processed_df = parser.parse_dataframe(
            df,
            name_column=name_column,
            add_components=True
        )

        # Add summary statistics
        stats = _calculate_processing_stats(processed_df)
        _display_stats(stats)

        # Determine output file
        if not output_file:
            output_file = input_file.stem + f"_processed.{format}"
            output_file = Path(output_file)

        # Save results
        _save_output(processed_df, output_file, format, show_confidence)

        console.print(f"[bold green]✓ Processing complete! Output saved to {output_file}[/bold green]")

    except Exception as e:
        logger.error(f"Error processing names: {e}")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def compare_parsers(
    names: list[str] = typer.Argument(..., help="Names to parse and compare"),
    save_results: bool = typer.Option(False, "--save", help="Save comparison results to CSV"),
    output_file: Path | None = typer.Option(None, "-o", "--output", help="Output file for comparison results"),
):
    """
    Compare parsing results across different parsers for given names.

    [bold green]Examples:[/bold green]

    [dim]# Compare parsing for specific names[/dim]
    python cli_demo.py compare-parsers "John Smith" "Rajesh Kumar Singh" "Dr. Mary Johnson-Brown"

    [dim]# Save comparison results[/dim]
    python cli_demo.py compare-parsers "Complex Name" --save -o comparison.csv
    """
    from search_names.enhanced_name_parser import (
        compare_parsers as compare_name_parsers,
    )

    console.print(f"[bold blue]Comparing parsers for {len(names)} names[/bold blue]")

    # Create comparison table
    table = Table(title="Parser Comparison Results")
    table.add_column("Name", style="cyan")
    table.add_column("Parser", style="magenta")
    table.add_column("First", style="green")
    table.add_column("Middle", style="blue")
    table.add_column("Last", style="yellow")
    table.add_column("Confidence", style="red")

    comparison_data = []

    for name in names:
        try:
            results = compare_name_parsers(name)

            for parser_name, result in results.items():
                table.add_row(
                    name if parser_name == list(results.keys())[0] else "",
                    parser_name,
                    result.first_name or "-",
                    result.middle_name or "-",
                    result.last_name or "-",
                    f"{result.confidence:.3f}"
                )

                comparison_data.append({
                    'name': name,
                    'parser': parser_name,
                    'first_name': result.first_name,
                    'middle_name': result.middle_name,
                    'last_name': result.last_name,
                    'title': result.title,
                    'suffix': result.suffix,
                    'confidence': result.confidence
                })

        except Exception as e:
            console.print(f"[red]Error processing '{name}': {e}[/red]")

    # Display results
    console.print(table)

    # Save results if requested
    if save_results:
        if not output_file:
            output_file = Path("parser_comparison.csv")

        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_csv(output_file, index=False)
        console.print(f"[green]Comparison results saved to {output_file}[/green]")


@app.command()
def generate_config(
    output_file: Path = typer.Option("name_config.yaml", "-o", "--output", help="Output configuration file"),
    parser_type: str = typer.Option("auto", help="Default parser type"),
    batch_size: int = typer.Option(100, help="Default batch size"),
    ml_threshold: float = typer.Option(0.8, help="ML confidence threshold"),
):
    """
    Generate a sample YAML configuration file.

    [bold green]Example:[/bold green]

    [dim]# Generate default configuration[/dim]
    python cli_demo.py generate-config -o my_config.yaml
    """
    config = NameCleaningConfig(
        parser_type=parser_type,
        batch_size=batch_size,
        ml_threshold=ml_threshold
    )

    # Create YAML content
    yaml_content = f"""# Name Processing Configuration
# Configuration for enhanced name parsing

# Parser selection: 'humanname', 'parsernaam', or 'auto'
# - humanname: Rule-based parser (always available)
# - parsernaam: ML-based parser (requires parsernaam package)
# - auto: Intelligent selection based on name patterns
parser_type: {config.parser_type}

# Batch size for processing names (affects parsernaam performance)
batch_size: {config.batch_size}

# Confidence threshold for ML predictions (0.0-1.0)
ml_threshold: {config.ml_threshold}

# Logging configuration
logging:
  level: INFO
  rich_logging: true

# Output formatting
output:
  include_confidence: true
  include_parser_info: true
  default_format: csv
"""

    output_file.write_text(yaml_content)
    console.print(f"[green]Configuration saved to {output_file}[/green]")
    console.print("[dim]Edit this file to customize processing behavior[/dim]")


@app.command()
def validate_names(
    input_file: Path = typer.Argument(..., help="Input CSV file"),
    name_column: str = typer.Option("Name", "-c", "--column", help="Column containing names"),
    min_confidence: float = typer.Option(0.7, help="Minimum confidence threshold"),
):
    """
    Validate name parsing quality and identify problematic names.

    [bold green]Example:[/bold green]

    [dim]# Validate names with default threshold[/dim]
    python cli_demo.py validate-names input.csv --min-confidence 0.8
    """
    console.print(f"[bold blue]Validating names in {input_file}[/bold blue]")

    try:
        df = pd.read_csv(input_file)

        if name_column not in df.columns:
            console.print(f"[red]Error: Column '{name_column}' not found[/red]")
            raise typer.Exit(1)

        # Parse with confidence scoring
        parser = NameParser(parser_type="auto")
        results = parser.parse(df[name_column].tolist())

        # Analyze results
        total_names = len(results)
        high_confidence = sum(1 for r in results if r.confidence >= min_confidence)
        low_confidence = total_names - high_confidence

        # Create validation table
        table = Table(title=f"Name Validation Results (threshold: {min_confidence})")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="magenta")
        table.add_column("Percentage", style="green")

        table.add_row("Total Names", str(total_names), "100.0%")
        table.add_row("High Confidence", str(high_confidence), f"{(high_confidence/total_names)*100:.1f}%")
        table.add_row("Low Confidence", str(low_confidence), f"{(low_confidence/total_names)*100:.1f}%")

        console.print(table)

        # Show problematic names
        if low_confidence > 0:
            console.print("\n[bold red]Names requiring attention:[/bold red]")
            problem_names = [(df[name_column].iloc[i], r.confidence)
                           for i, r in enumerate(results) if r.confidence < min_confidence]

            for name, confidence in problem_names[:10]:  # Show first 10
                console.print(f"  [red]'{name}'[/red] (confidence: {confidence:.3f})")

            if len(problem_names) > 10:
                console.print(f"  [dim]... and {len(problem_names) - 10} more[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


def _calculate_processing_stats(df: pd.DataFrame) -> dict:
    """Calculate processing statistics."""
    stats = {}

    if 'parsed_confidence' in df.columns:
        stats['avg_confidence'] = df['parsed_confidence'].mean()
        stats['min_confidence'] = df['parsed_confidence'].min()
        stats['high_confidence_count'] = (df['parsed_confidence'] >= 0.8).sum()

    if 'parser_used' in df.columns:
        stats['parser_usage'] = df['parser_used'].value_counts().to_dict()

    stats['total_processed'] = len(df)
    stats['successful_parses'] = len(df.dropna(subset=['parsed_first_name', 'parsed_last_name']))

    return stats


def _display_stats(stats: dict):
    """Display processing statistics."""
    table = Table(title="Processing Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Total Processed", str(stats['total_processed']))
    table.add_row("Successful Parses", str(stats['successful_parses']))

    if 'avg_confidence' in stats:
        table.add_row("Average Confidence", f"{stats['avg_confidence']:.3f}")
        table.add_row("Minimum Confidence", f"{stats['min_confidence']:.3f}")
        table.add_row("High Confidence (≥0.8)", str(stats['high_confidence_count']))

    if 'parser_usage' in stats:
        for parser, count in stats['parser_usage'].items():
            table.add_row(f"Used {parser}", str(count))

    console.print(table)


def _save_output(df: pd.DataFrame, output_file: Path, format_type: str, include_confidence: bool):
    """Save output in specified format."""
    # Filter columns if confidence not requested
    if not include_confidence:
        confidence_cols = [col for col in df.columns if 'confidence' in col.lower()]
        df = df.drop(columns=confidence_cols, errors='ignore')

    try:
        if format_type.lower() == 'csv':
            df.to_csv(output_file, index=False)
        elif format_type.lower() == 'json':
            df.to_json(output_file, orient='records', indent=2)
        elif format_type.lower() == 'parquet':
            try:
                df.to_parquet(output_file, index=False)
            except ImportError:
                console.print("[yellow]Warning: Parquet support requires pyarrow. Falling back to CSV.[/yellow]")
                output_file = output_file.with_suffix('.csv')
                df.to_csv(output_file, index=False)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    except Exception as e:
        raise Exception(f"Failed to save output: {e}") from e


if __name__ == "__main__":
    app()
