"""Pydantic models for data validation in search_names package."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


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
    first_name: str | None = Field(None, description="First name")
    middle_name: str | None = Field(None, description="Middle name or initial")
    last_name: str | None = Field(None, description="Last name")
    prefix: str | None = Field(None, description="Title or prefix (Mr., Dr., etc.)")
    suffix: str | None = Field(None, description="Suffix (Jr., Sr., III, etc.)")
    roman_numeral: str | None = Field(None, description="Roman numeral")
    original_name: str = Field(..., description="Original name as provided")

    @field_validator("uniqid")
    @classmethod
    def uniqid_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("uniqid cannot be empty")
        return v.strip()

    @field_validator("original_name")
    @classmethod
    def original_name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("original_name cannot be empty")
        return v.strip()


class SupplementaryData(BaseModel):
    """Model for supplementary name data."""

    prefixes: str | None = Field(None, description="Semi-colon separated prefixes")
    nick_names: str | None = Field(None, description="Semi-colon separated nicknames")
    aliases: str | None = Field(None, description="Semi-colon separated aliases")

    @field_validator("prefixes", "nick_names", "aliases", mode="before")
    @classmethod
    def clean_string_lists(cls, v):
        if v is None:
            return v
        if isinstance(v, list):
            return ";".join(str(item).strip() for item in v if str(item).strip())
        return str(v).strip()


class SearchPattern(BaseModel):
    """Model for search patterns."""

    pattern: str = Field(..., description="Search pattern (e.g., 'FirstName LastName')")
    uniqid: str = Field(..., description="Unique identifier")
    search_name: str = Field(..., description="Actual name to search for")
    confidence: float | None = Field(None, ge=0.0, le=1.0, description="Confidence score")

    @field_validator("pattern")
    @classmethod
    def pattern_must_be_valid(cls, v):
        valid_patterns = {e.value for e in NameFormat}
        if v not in valid_patterns:
            raise ValueError(f"pattern must be one of {valid_patterns}")
        return v


class SearchResult(BaseModel):
    """Model for search results."""

    uniqid: str = Field(..., description="Unique identifier from search list")
    match_count: int = Field(0, ge=0, description="Number of matches found")
    matches: list[str] = Field(default_factory=list, description="Matched text")
    start_positions: list[int] = Field(default_factory=list, description="Start positions")
    end_positions: list[int] = Field(default_factory=list, description="End positions")
    confidence_scores: list[float] = Field(default_factory=list, description="Confidence scores")

    @model_validator(mode="after")
    def validate_list_lengths(self):
        """Ensure all lists have the same length."""
        match_count = self.match_count
        matches = self.matches
        starts = self.start_positions
        ends = self.end_positions
        scores = self.confidence_scores

        if match_count != len(matches):
            raise ValueError("match_count must equal length of matches list")

        if len(matches) != len(starts) or len(matches) != len(ends):
            raise ValueError("matches, start_positions, and end_positions must have same length")

        if scores and len(scores) != len(matches):
            raise ValueError("confidence_scores must be empty or same length as matches")

        return self


class TextDocument(BaseModel):
    """Model for text documents to be searched."""

    uniqid: str = Field(..., description="Unique identifier for the document")
    text: str = Field(..., description="Text content to search")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    preprocessed_text: str | None = Field(None, description="Preprocessed text")

    @field_validator("uniqid")
    @classmethod
    def uniqid_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("uniqid cannot be empty")
        return v.strip()

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("text cannot be empty")
        return v.strip()


class SearchJobConfig(BaseModel):
    """Model for search job configuration."""

    name_file: str = Field(..., description="Path to names file")
    text_file: str = Field(..., description="Path to text corpus file")
    output_file: str = Field(..., description="Path to output file")
    max_results: int = Field(20, ge=1, description="Maximum results per document")
    processes: int = Field(4, ge=1, description="Number of parallel processes")
    chunk_size: int = Field(1000, ge=1, description="Chunk size for processing")
    fuzzy_min_lengths: list[list] = Field(
        default_factory=list, description="Fuzzy matching parameters"
    )
    clean_text: bool = Field(False, description="Whether to clean text before search")
    input_columns: list[str] = Field(default_factory=list, description="Input columns to include")
    search_columns: list[str] = Field(default_factory=list, description="Search result columns")

    @field_validator("fuzzy_min_lengths")
    @classmethod
    def validate_fuzzy_lengths(cls, v):
        for item in v:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                raise ValueError("fuzzy_min_lengths must contain tuples/lists of length 2")
            if not isinstance(item[0], int) or not isinstance(item[1], int):
                raise ValueError("fuzzy_min_lengths values must be integers")
            if item[0] <= 0 or item[1] < 0:
                raise ValueError("fuzzy_min_lengths must be positive integers")
        return v


class NameSearchJob(BaseModel):
    """Model for a complete name search job."""

    job_id: str = Field(..., description="Unique job identifier")
    config: SearchJobConfig = Field(..., description="Job configuration")
    status: str = Field("pending", description="Job status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    started_at: datetime | None = Field(None, description="Start timestamp")
    completed_at: datetime | None = Field(None, description="Completion timestamp")
    error_message: str | None = Field(None, description="Error message if failed")
    results_count: int = Field(0, ge=0, description="Total number of results")

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        valid_statuses = {"pending", "running", "completed", "failed"}
        if v not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}")
        return v


class FuzzyMatchConfig(BaseModel):
    """Model for fuzzy matching configuration."""

    min_length: int = Field(..., ge=1, description="Minimum string length for this edit distance")
    edit_distance: int = Field(..., ge=0, description="Maximum edit distance allowed")

    @model_validator(mode="after")
    def edit_distance_reasonable(self):
        if self.edit_distance > self.min_length // 2:
            raise ValueError("edit_distance should not exceed half the min_length")
        return self


class EntityMention(BaseModel):
    """Model for entity mentions found by NER."""

    text: str = Field(..., description="Mention text")
    label: str = Field(..., description="Entity label (PERSON, ORG, etc.)")
    start: int = Field(..., ge=0, description="Start position in text")
    end: int = Field(..., ge=0, description="End position in text")
    confidence: float | None = Field(None, ge=0.0, le=1.0, description="Confidence score")

    @model_validator(mode="after")
    def validate_positions(self):
        if self.end <= self.start:
            raise ValueError("end position must be greater than start position")
        return self


class EntityLinkingResult(BaseModel):
    """Model for entity linking results."""

    mention: EntityMention = Field(..., description="Original mention")
    linked_entity_id: str | None = Field(None, description="Linked entity ID")
    linked_entity_name: str | None = Field(None, description="Canonical entity name")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Linking confidence")
    alternative_entities: list[dict[str, Any]] = Field(
        default_factory=list, description="Alternative entity candidates"
    )


class ProcessingStats(BaseModel):
    """Model for processing statistics."""

    total_documents: int = Field(0, ge=0)
    processed_documents: int = Field(0, ge=0)
    total_matches: int = Field(0, ge=0)
    processing_time_seconds: float = Field(0.0, ge=0.0)
    documents_per_second: float = Field(0.0, ge=0.0)
    errors_count: int = Field(0, ge=0)
    warnings_count: int = Field(0, ge=0)

    @model_validator(mode="after")
    def calculate_derived_stats(self):
        if self.processing_time_seconds > 0:
            self.documents_per_second = self.processed_documents / self.processing_time_seconds
        else:
            self.documents_per_second = 0.0
        return self


# Input/Output models for API endpoints


class SearchRequest(BaseModel):
    """Model for search API requests."""

    documents: list[TextDocument] = Field(..., min_length=1)
    search_patterns: list[SearchPattern] = Field(..., min_length=1)
    config: SearchJobConfig | None = Field(None)


class SearchResponse(BaseModel):
    """Model for search API responses."""

    job_id: str
    results: list[SearchResult]
    stats: ProcessingStats
    status: str = "completed"
    message: str | None = None
