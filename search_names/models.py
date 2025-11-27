"""Pydantic models for data validation in search_names package."""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
from enum import Enum


class NameFormat(str, Enum):
    """Enumeration of supported name formats."""
    FIRST_LAST = "FirstName LastName"
    LAST_FIRST = "LastName, FirstName"
    NICK_LAST = "NickName LastName"
    PREFIX_LAST = "Prefix LastName"
    FULL = "FirstName MiddleName LastName"
    INFORMAL = "FirstName"


class FileFormat(str, Enum):
    """Enumeration of supported file formats."""
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    EXCEL = "xlsx"


class LogLevel(str, Enum):
    """Enumeration of supported log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CleanedName(BaseModel):
    """Model for a cleaned name record."""
    uniqid: str = Field(..., description="Unique identifier for the name")
    first_name: Optional[str] = Field(None, description="First name")
    middle_name: Optional[str] = Field(None, description="Middle name or initial")
    last_name: Optional[str] = Field(None, description="Last name")
    prefix: Optional[str] = Field(None, description="Title or prefix (Mr., Dr., etc.)")
    suffix: Optional[str] = Field(None, description="Suffix (Jr., Sr., III, etc.)")
    roman_numeral: Optional[str] = Field(None, description="Roman numeral")
    original_name: str = Field(..., description="Original name as provided")
    
    @validator('uniqid')
    def uniqid_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('uniqid cannot be empty')
        return v.strip()
    
    @validator('original_name')
    def original_name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('original_name cannot be empty')
        return v.strip()


class SupplementaryData(BaseModel):
    """Model for supplementary name data."""
    prefixes: Optional[str] = Field(None, description="Semi-colon separated prefixes")
    nick_names: Optional[str] = Field(None, description="Semi-colon separated nicknames")
    aliases: Optional[str] = Field(None, description="Semi-colon separated aliases")
    
    @validator('prefixes', 'nick_names', 'aliases', pre=True)
    def clean_string_lists(cls, v):
        if v is None:
            return v
        if isinstance(v, list):
            return ';'.join(str(item).strip() for item in v if str(item).strip())
        return str(v).strip()


class SearchPattern(BaseModel):
    """Model for search patterns."""
    pattern: str = Field(..., description="Search pattern (e.g., 'FirstName LastName')")
    uniqid: str = Field(..., description="Unique identifier")
    search_name: str = Field(..., description="Actual name to search for")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    
    @validator('pattern')
    def pattern_must_be_valid(cls, v):
        valid_patterns = {e.value for e in NameFormat}
        if v not in valid_patterns:
            raise ValueError(f'pattern must be one of {valid_patterns}')
        return v


class SearchResult(BaseModel):
    """Model for search results."""
    uniqid: str = Field(..., description="Unique identifier from search list")
    match_count: int = Field(0, ge=0, description="Number of matches found")
    matches: List[str] = Field(default_factory=list, description="Matched text")
    start_positions: List[int] = Field(default_factory=list, description="Start positions")
    end_positions: List[int] = Field(default_factory=list, description="End positions")
    confidence_scores: List[float] = Field(default_factory=list, description="Confidence scores")
    
    @root_validator
    def validate_list_lengths(cls, values):
        """Ensure all lists have the same length."""
        match_count = values.get('match_count', 0)
        matches = values.get('matches', [])
        starts = values.get('start_positions', [])
        ends = values.get('end_positions', [])
        scores = values.get('confidence_scores', [])
        
        if match_count != len(matches):
            raise ValueError('match_count must equal length of matches list')
        
        if len(matches) != len(starts) or len(matches) != len(ends):
            raise ValueError('matches, start_positions, and end_positions must have same length')
        
        if scores and len(scores) != len(matches):
            raise ValueError('confidence_scores must be empty or same length as matches')
        
        return values


class TextDocument(BaseModel):
    """Model for text documents to be searched."""
    uniqid: str = Field(..., description="Unique identifier for the document")
    text: str = Field(..., description="Text content to search")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    preprocessed_text: Optional[str] = Field(None, description="Preprocessed text")
    
    @validator('uniqid')
    def uniqid_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('uniqid cannot be empty')
        return v.strip()
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('text cannot be empty')
        return v.strip()


class SearchJobConfig(BaseModel):
    """Model for search job configuration."""
    name_file: str = Field(..., description="Path to names file")
    text_file: str = Field(..., description="Path to text corpus file")
    output_file: str = Field(..., description="Path to output file")
    max_results: int = Field(20, ge=1, description="Maximum results per document")
    processes: int = Field(4, ge=1, description="Number of parallel processes")
    chunk_size: int = Field(1000, ge=1, description="Chunk size for processing")
    fuzzy_min_lengths: List[tuple] = Field(default_factory=list, description="Fuzzy matching parameters")
    clean_text: bool = Field(False, description="Whether to clean text before search")
    input_columns: List[str] = Field(default_factory=list, description="Input columns to include")
    search_columns: List[str] = Field(default_factory=list, description="Search result columns")
    
    @validator('fuzzy_min_lengths')
    def validate_fuzzy_lengths(cls, v):
        for item in v:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                raise ValueError('fuzzy_min_lengths must contain tuples/lists of length 2')
            if not isinstance(item[0], int) or not isinstance(item[1], int):
                raise ValueError('fuzzy_min_lengths values must be integers')
            if item[0] <= 0 or item[1] < 0:
                raise ValueError('fuzzy_min_lengths must be positive integers')
        return v


class NameSearchJob(BaseModel):
    """Model for a complete name search job."""
    job_id: str = Field(..., description="Unique job identifier")
    config: SearchJobConfig = Field(..., description="Job configuration")
    status: str = Field("pending", description="Job status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    results_count: int = Field(0, ge=0, description="Total number of results")
    
    @validator('status')
    def status_must_be_valid(cls, v):
        valid_statuses = {'pending', 'running', 'completed', 'failed'}
        if v not in valid_statuses:
            raise ValueError(f'status must be one of {valid_statuses}')
        return v


class FuzzyMatchConfig(BaseModel):
    """Model for fuzzy matching configuration."""
    min_length: int = Field(..., ge=1, description="Minimum string length for this edit distance")
    edit_distance: int = Field(..., ge=0, description="Maximum edit distance allowed")
    
    @validator('edit_distance')
    def edit_distance_reasonable(cls, v, values):
        min_length = values.get('min_length', 0)
        if v > min_length // 2:
            raise ValueError('edit_distance should not exceed half the min_length')
        return v


class EntityMention(BaseModel):
    """Model for entity mentions found by NER."""
    text: str = Field(..., description="Mention text")
    label: str = Field(..., description="Entity label (PERSON, ORG, etc.)")
    start: int = Field(..., ge=0, description="Start position in text")
    end: int = Field(..., ge=0, description="End position in text")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    
    @root_validator
    def validate_positions(cls, values):
        start = values.get('start', 0)
        end = values.get('end', 0)
        if end <= start:
            raise ValueError('end position must be greater than start position')
        return values


class EntityLinkingResult(BaseModel):
    """Model for entity linking results."""
    mention: EntityMention = Field(..., description="Original mention")
    linked_entity_id: Optional[str] = Field(None, description="Linked entity ID")
    linked_entity_name: Optional[str] = Field(None, description="Canonical entity name")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Linking confidence")
    alternative_entities: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative entity candidates")


class ProcessingStats(BaseModel):
    """Model for processing statistics."""
    total_documents: int = Field(0, ge=0)
    processed_documents: int = Field(0, ge=0)
    total_matches: int = Field(0, ge=0)
    processing_time_seconds: float = Field(0.0, ge=0.0)
    documents_per_second: float = Field(0.0, ge=0.0)
    errors_count: int = Field(0, ge=0)
    warnings_count: int = Field(0, ge=0)
    
    @root_validator
    def calculate_derived_stats(cls, values):
        processed = values.get('processed_documents', 0)
        time_taken = values.get('processing_time_seconds', 0.0)
        
        if time_taken > 0:
            values['documents_per_second'] = processed / time_taken
        else:
            values['documents_per_second'] = 0.0
        
        return values
    
    
# Input/Output models for API endpoints

class SearchRequest(BaseModel):
    """Model for search API requests."""
    documents: List[TextDocument] = Field(..., min_items=1)
    search_patterns: List[SearchPattern] = Field(..., min_items=1)
    config: Optional[SearchJobConfig] = Field(None)


class SearchResponse(BaseModel):
    """Model for search API responses."""
    job_id: str
    results: List[SearchResult]
    stats: ProcessingStats
    status: str = "completed"
    message: Optional[str] = None