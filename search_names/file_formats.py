"""Support for multiple file formats (CSV, JSON, Parquet) in search_names package."""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pandas as pd

from .logging_config import get_logger

logger = get_logger("file_formats")

# Optional imports with fallbacks
try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    HAS_PARQUET = True
except ImportError:
    logger.debug("pyarrow not available - Parquet support disabled")
    HAS_PARQUET = False

try:
    import polars as pl
    HAS_POLARS = True
except ImportError:
    logger.debug("polars not available - using pandas only")
    HAS_POLARS = False


class FileFormatError(Exception):
    """Exception raised for file format related errors."""
    pass


def detect_file_format(file_path: str | Path) -> str:
    """Detect file format from extension.

    Args:
        file_path: Path to the file

    Returns:
        File format: 'csv', 'json', 'parquet', or 'excel'

    Raises:
        FileFormatError: If format is not supported
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    format_map = {
        '.csv': 'csv',
        '.json': 'json',
        '.jsonl': 'json',
        '.parquet': 'parquet',
        '.pq': 'parquet',
        '.xlsx': 'excel',
        '.xls': 'excel',
    }

    if suffix not in format_map:
        raise FileFormatError(f"Unsupported file format: {suffix}")

    file_format = format_map[suffix]

    # Check if format is available
    if file_format == 'parquet' and not HAS_PARQUET:
        raise FileFormatError("Parquet support requires pyarrow: pip install pyarrow")

    return file_format


def read_file(
    file_path: str | Path,
    file_format: str | None = None,
    engine: str = "pandas",
    **kwargs
) -> pd.DataFrame:
    """Read file in various formats into a pandas DataFrame.

    Args:
        file_path: Path to the input file
        file_format: File format ('csv', 'json', 'parquet', 'excel').
                    Auto-detected if None.
        engine: Engine to use ('pandas' or 'polars')
        **kwargs: Additional arguments passed to the reader

    Returns:
        DataFrame with the data

    Raises:
        FileFormatError: If format is not supported or file cannot be read
    """
    path = Path(file_path)

    if not path.exists():
        raise FileFormatError(f"File does not exist: {path}")

    if file_format is None:
        file_format = detect_file_format(path)

    logger.info(f"Reading {file_format} file: {path}")

    try:
        if engine == "polars" and HAS_POLARS:
            return _read_file_polars(path, file_format, **kwargs)
        else:
            return _read_file_pandas(path, file_format, **kwargs)
    except Exception as e:
        raise FileFormatError(f"Error reading {file_format} file {path}: {e}") from e


def _read_file_pandas(path: Path, file_format: str, **kwargs) -> pd.DataFrame:
    """Read file using pandas."""
    if file_format == 'csv':
        # Set sensible defaults for CSV
        csv_kwargs = {
            'encoding': 'utf-8',
            'na_values': ['', 'NA', 'NULL', 'null', 'None'],
            'keep_default_na': True,
        }
        csv_kwargs.update(kwargs)
        return pd.read_csv(path, **csv_kwargs)

    elif file_format == 'json':
        # Handle both regular JSON and JSON Lines
        json_kwargs = {'encoding': 'utf-8'}
        json_kwargs.update(kwargs)

        # Try JSON Lines first (more common for large datasets)
        try:
            return pd.read_json(path, lines=True, **json_kwargs)
        except ValueError:
            # Fall back to regular JSON
            return pd.read_json(path, **json_kwargs)

    elif file_format == 'parquet':
        if not HAS_PARQUET:
            raise FileFormatError("Parquet support requires pyarrow")
        return pd.read_parquet(path, **kwargs)

    elif file_format == 'excel':
        excel_kwargs = {'engine': 'openpyxl'}
        excel_kwargs.update(kwargs)
        return pd.read_excel(path, **excel_kwargs)

    else:
        raise FileFormatError(f"Unsupported format for pandas: {file_format}")


def _read_file_polars(path: Path, file_format: str, **kwargs) -> pd.DataFrame:
    """Read file using polars (converted to pandas for compatibility)."""
    if file_format == 'csv':
        df = pl.read_csv(path, **kwargs)
    elif file_format == 'json':
        df = pl.read_json(path, **kwargs)
    elif file_format == 'parquet':
        df = pl.read_parquet(path, **kwargs)
    else:
        raise FileFormatError(f"Polars does not support format: {file_format}")

    # Convert to pandas for compatibility
    return df.to_pandas()


def write_file(
    df: pd.DataFrame,
    file_path: str | Path,
    file_format: str | None = None,
    engine: str = "pandas",
    **kwargs
) -> None:
    """Write DataFrame to file in various formats.

    Args:
        df: DataFrame to write
        file_path: Output file path
        file_format: File format ('csv', 'json', 'parquet').
                    Auto-detected if None.
        engine: Engine to use ('pandas' or 'polars')
        **kwargs: Additional arguments passed to the writer

    Raises:
        FileFormatError: If format is not supported or file cannot be written
    """
    path = Path(file_path)

    if file_format is None:
        file_format = detect_file_format(path)

    # Ensure output directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Writing {file_format} file: {path}")

    try:
        if engine == "polars" and HAS_POLARS:
            _write_file_polars(df, path, file_format, **kwargs)
        else:
            _write_file_pandas(df, path, file_format, **kwargs)
    except Exception as e:
        raise FileFormatError(f"Error writing {file_format} file {path}: {e}") from e


def _write_file_pandas(df: pd.DataFrame, path: Path, file_format: str, **kwargs) -> None:
    """Write file using pandas."""
    if file_format == 'csv':
        csv_kwargs = {
            'index': False,
            'encoding': 'utf-8',
        }
        csv_kwargs.update(kwargs)
        df.to_csv(path, **csv_kwargs)

    elif file_format == 'json':
        json_kwargs = {
            'orient': 'records',
            'lines': True,  # JSON Lines format for better performance
            'force_ascii': False,
        }
        json_kwargs.update(kwargs)
        df.to_json(path, **json_kwargs)

    elif file_format == 'parquet':
        if not HAS_PARQUET:
            raise FileFormatError("Parquet support requires pyarrow")
        parquet_kwargs = {
            'index': False,
            'compression': 'snappy',  # Good compression/speed tradeoff
        }
        parquet_kwargs.update(kwargs)
        df.to_parquet(path, **parquet_kwargs)

    else:
        raise FileFormatError(f"Unsupported format for pandas: {file_format}")


def _write_file_polars(df: pd.DataFrame, path: Path, file_format: str, **kwargs) -> None:
    """Write file using polars."""
    # Convert pandas to polars
    pl_df = pl.from_pandas(df)

    if file_format == 'csv':
        pl_df.write_csv(path, **kwargs)
    elif file_format == 'json':
        pl_df.write_json(path, **kwargs)
    elif file_format == 'parquet':
        pl_df.write_parquet(path, **kwargs)
    else:
        raise FileFormatError(f"Polars does not support format: {file_format}")


def read_file_chunked(
    file_path: str | Path,
    chunk_size: int = 10000,
    file_format: str | None = None,
    **kwargs
) -> Iterator[pd.DataFrame]:
    """Read file in chunks to handle large datasets.

    Args:
        file_path: Path to the input file
        chunk_size: Number of rows per chunk
        file_format: File format. Auto-detected if None.
        **kwargs: Additional arguments passed to the reader

    Yields:
        DataFrame chunks

    Raises:
        FileFormatError: If format is not supported or file cannot be read
    """
    path = Path(file_path)

    if file_format is None:
        file_format = detect_file_format(path)

    logger.info(f"Reading {file_format} file in chunks: {path}")

    if file_format == 'csv':
        csv_kwargs = {
            'encoding': 'utf-8',
            'chunksize': chunk_size,
            'na_values': ['', 'NA', 'NULL', 'null', 'None'],
        }
        csv_kwargs.update(kwargs)

        try:
            for chunk in pd.read_csv(path, **csv_kwargs):
                yield chunk
        except Exception as e:
            raise FileFormatError(f"Error reading CSV chunks from {path}: {e}") from e

    elif file_format == 'json':
        # JSON Lines format supports chunked reading
        json_kwargs = {
            'lines': True,
            'chunksize': chunk_size,
        }
        json_kwargs.update(kwargs)

        try:
            for chunk in pd.read_json(path, **json_kwargs):
                yield chunk
        except Exception as e:
            raise FileFormatError(f"Error reading JSON chunks from {path}: {e}") from e

    elif file_format == 'parquet':
        if not HAS_PARQUET:
            raise FileFormatError("Parquet support requires pyarrow")

        try:
            parquet_file = pq.ParquetFile(path)
            for batch in parquet_file.iter_batches(batch_size=chunk_size):
                yield batch.to_pandas()
        except Exception as e:
            raise FileFormatError(f"Error reading Parquet chunks from {path}: {e}") from e

    else:
        raise FileFormatError(f"Chunked reading not supported for format: {file_format}")


def get_file_info(file_path: str | Path) -> dict[str, Any]:
    """Get information about a file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file information
    """
    path = Path(file_path)

    if not path.exists():
        raise FileFormatError(f"File does not exist: {path}")

    info = {
        'path': str(path),
        'size_bytes': path.stat().st_size,
        'size_mb': round(path.stat().st_size / 1024 / 1024, 2),
        'format': None,
        'rows': None,
        'columns': None,
        'column_names': None,
    }

    try:
        file_format = detect_file_format(path)
        info['format'] = file_format

        # Get row/column info for supported formats
        if file_format in ['csv', 'json', 'parquet']:
            # Read just the first few rows to get structure
            try:
                df_sample = read_file(path, file_format).head(1)
                info['columns'] = len(df_sample.columns)
                info['column_names'] = list(df_sample.columns)

                # For smaller files, get exact row count
                if info['size_mb'] < 100:  # Only for files < 100MB
                    df_full = read_file(path, file_format)
                    info['rows'] = len(df_full)
                else:
                    info['rows'] = "Large file - use chunked reading"

            except Exception as e:
                logger.warning(f"Could not read file structure: {e}")

    except Exception as e:
        logger.warning(f"Could not detect file format: {e}")

    return info


# Convenience functions for common use cases

def csv_to_json(input_path: str | Path, output_path: str | Path, **kwargs) -> None:
    """Convert CSV file to JSON format."""
    df = read_file(input_path, 'csv')
    write_file(df, output_path, 'json', **kwargs)


def csv_to_parquet(input_path: str | Path, output_path: str | Path, **kwargs) -> None:
    """Convert CSV file to Parquet format."""
    df = read_file(input_path, 'csv')
    write_file(df, output_path, 'parquet', **kwargs)


def json_to_csv(input_path: str | Path, output_path: str | Path, **kwargs) -> None:
    """Convert JSON file to CSV format."""
    df = read_file(input_path, 'json')
    write_file(df, output_path, 'csv', **kwargs)


def parquet_to_csv(input_path: str | Path, output_path: str | Path, **kwargs) -> None:
    """Convert Parquet file to CSV format."""
    df = read_file(input_path, 'parquet')
    write_file(df, output_path, 'csv', **kwargs)
