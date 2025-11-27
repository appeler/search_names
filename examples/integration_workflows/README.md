# Integration Workflows

This directory demonstrates complete end-to-end workflows using all components of the modernized search_names package.

## Workflows Demonstrated

### Complete Name Processing Pipeline
- Load raw name data
- Configure enhanced name parsing
- Process with intelligent parser selection  
- Generate statistics and quality metrics
- Export results in multiple formats

### Multi-Format Data Export
- CSV for compatibility
- JSON for APIs and web applications
- Parquet for big data analytics (optional)
- Excel for business users (optional)

### Batch Processing Optimization
- Performance testing with different batch sizes
- Memory-efficient processing of large datasets
- Timing and throughput metrics
- Resource utilization monitoring

### Error Handling and Validation
- Graceful handling of problematic inputs
- Data quality assessment
- Error reporting and logging
- Recovery strategies

### Configuration-Driven Processing
- Environment-specific configurations
- Use-case optimized settings
- A/B testing different approaches
- Performance tuning

## Key Benefits

### Modern Python Integration
- Type-safe pandas DataFrame operations
- Pydantic data validation
- Rich logging and progress indicators
- Configurable processing pipelines

### Production Ready
- Comprehensive error handling
- Performance monitoring
- Memory efficient processing
- Scalable batch operations

### Flexible Output
- Multiple format support
- Configurable output schemas
- Quality metrics and statistics
- Audit trails and logging

## Usage

Run the complete workflow demo:
```bash
cd examples/integration_workflows
python complete_workflow_demo.py
```

This will demonstrate:
1. Processing political candidate names
2. Exporting to multiple formats
3. Batch processing performance
4. Error handling scenarios
5. Configuration comparisons

## Integration Examples

### With Data Pipelines
```python
from search_names.enhanced_name_parser import NameParser
import pandas as pd

def process_name_data(input_file, output_file, config):
    # Load data
    df = pd.read_csv(input_file)
    
    # Configure parser
    parser = NameParser(**config)
    
    # Process names
    enhanced_df = parser.parse_dataframe(df, name_column="name")
    
    # Save results
    enhanced_df.to_parquet(output_file, index=False)
    
    return enhanced_df
```

### With APIs
```python
from search_names.enhanced_name_parser import parse_names
from search_names.models import CleanedName

def api_name_processing(names: List[str]) -> List[CleanedName]:
    results = parse_names(names, parser_type="auto")
    return [r.to_dict() for r in results]
```

### With Databases
```python
import sqlalchemy as sa
from search_names.enhanced_name_parser import NameParser

def process_database_names(connection, table_name):
    # Read from database
    df = pd.read_sql(f"SELECT * FROM {table_name}", connection)
    
    # Process names
    parser = NameParser(parser_type="auto")
    processed_df = parser.parse_dataframe(df, name_column="raw_name")
    
    # Write back to database
    processed_df.to_sql(f"{table_name}_processed", connection, 
                       if_exists="replace", index=False)
```

This demonstrates the package's flexibility and production readiness for real-world data processing workflows.