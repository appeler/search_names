"""Enhanced name parser with support for both HumanName and parsernaam."""

from typing import List, Dict, Any, Optional, Union, Tuple
import pandas as pd
from dataclasses import dataclass

try:
    from .logging_config import get_logger
    logger = get_logger("enhanced_name_parser")
except ImportError:
    # Fallback for when module is imported directly
    import logging
    logger = logging.getLogger("enhanced_name_parser")

# Import nameparser (always available)
from nameparser import HumanName

# Try importing parsernaam
try:
    from parsernaam.parse import ParseNames
    HAS_PARSERNAAM = True
except ImportError:
    logger.debug("parsernaam not available - ML-based name parsing disabled")
    HAS_PARSERNAAM = False


@dataclass
class ParsedName:
    """Unified parsed name representation."""
    original: str
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    suffix: Optional[str] = None
    nickname: Optional[str] = None
    confidence: float = 1.0
    parser_used: str = "humanname"
    
    def full_name(self) -> str:
        """Get full name from components."""
        parts = []
        if self.title:
            parts.append(self.title)
        if self.first_name:
            parts.append(self.first_name)
        if self.middle_name:
            parts.append(self.middle_name)
        if self.last_name:
            parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original": self.original,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "title": self.title,
            "suffix": self.suffix,
            "nickname": self.nickname,
            "confidence": self.confidence,
            "parser_used": self.parser_used,
        }


class NameParser:
    """Enhanced name parser with multiple backend support."""
    
    def __init__(
        self, 
        parser_type: str = "auto",
        batch_size: int = 100,
        ml_threshold: float = 0.8
    ):
        """Initialize name parser.
        
        Args:
            parser_type: "humanname", "parsernaam", or "auto"
            batch_size: Batch size for parsernaam processing
            ml_threshold: Confidence threshold for ML predictions
        """
        self.parser_type = parser_type
        self.batch_size = batch_size
        self.ml_threshold = ml_threshold
        
        # Validate parser availability
        if parser_type == "parsernaam" and not HAS_PARSERNAAM:
            logger.warning("parsernaam requested but not available, falling back to humanname")
            self.parser_type = "humanname"
        
        logger.info(f"Initialized NameParser with type: {self.parser_type}")
    
    def parse_with_humanname(self, name: str) -> ParsedName:
        """Parse name using HumanName."""
        try:
            parsed = HumanName(name)
            
            return ParsedName(
                original=name,
                first_name=parsed.first if parsed.first else None,
                middle_name=parsed.middle if parsed.middle else None,
                last_name=parsed.last if parsed.last else None,
                title=parsed.title if parsed.title else None,
                suffix=parsed.suffix if parsed.suffix else None,
                nickname=parsed.nickname if parsed.nickname else None,
                confidence=1.0,
                parser_used="humanname"
            )
        except Exception as e:
            logger.error(f"Error parsing name '{name}' with HumanName: {e}")
            return ParsedName(original=name, confidence=0.0, parser_used="humanname")
    
    def parse_with_parsernaam(self, names: List[str]) -> List[ParsedName]:
        """Parse names using parsernaam (batch processing)."""
        if not HAS_PARSERNAAM:
            logger.warning("parsernaam not available, using humanname")
            return [self.parse_with_humanname(name) for name in names]
        
        try:
            # Create DataFrame for parsernaam
            df = pd.DataFrame({'name': names})
            
            # Parse names
            results = ParseNames.parse(df)
            
            # Convert results to ParsedName objects
            parsed_names = []
            for idx, row in results.iterrows():
                # parsernaam returns predictions for each token
                # We need to reconstruct the name components
                name_parts = self._extract_name_parts_from_parsernaam(row)
                
                parsed_names.append(ParsedName(
                    original=names[idx],
                    first_name=name_parts.get('first_name'),
                    middle_name=name_parts.get('middle_name'),
                    last_name=name_parts.get('last_name'),
                    confidence=name_parts.get('confidence', 0.8),
                    parser_used="parsernaam"
                ))
            
            return parsed_names
            
        except Exception as e:
            logger.error(f"Error parsing names with parsernaam: {e}")
            # Fall back to humanname
            return [self.parse_with_humanname(name) for name in names]
    
    def _extract_name_parts_from_parsernaam(self, row: pd.Series) -> Dict[str, Any]:
        """Extract name parts from parsernaam output."""
        # parsernaam returns predictions for each word
        # This is a simplified extraction - could be enhanced
        parts = {
            'first_name': None,
            'middle_name': None,
            'last_name': None,
            'confidence': 0.8
        }
        
        # Extract based on parsernaam's predictions
        # Note: This depends on parsernaam's actual output format
        # which may need adjustment based on the library's API
        try:
            if 'first_name' in row:
                parts['first_name'] = row['first_name']
            if 'last_name' in row:
                parts['last_name'] = row['last_name']
            if 'confidence' in row:
                parts['confidence'] = row['confidence']
        except Exception:
            pass
        
        return parts
    
    def is_indian_name(self, name: str) -> bool:
        """Check if name appears to be Indian."""
        # Common Indian name patterns and suffixes
        indian_patterns = [
            'kumar', 'kumari', 'devi', 'singh', 'das', 'rao', 'reddy',
            'sharma', 'gupta', 'patel', 'shah', 'mehta', 'varma',
            'krishna', 'ram', 'sai', 'venkat', 'raj', 'mohan',
            'swamy', 'naidu', 'choudhury', 'mukherjee', 'chatterjee'
        ]
        
        name_lower = name.lower()
        return any(pattern in name_lower for pattern in indian_patterns)
    
    def parse(self, name: Union[str, List[str]]) -> Union[ParsedName, List[ParsedName]]:
        """Parse one or more names.
        
        Args:
            name: Single name string or list of names
            
        Returns:
            ParsedName or list of ParsedName objects
        """
        # Handle single name
        if isinstance(name, str):
            if self.parser_type == "humanname":
                return self.parse_with_humanname(name)
            elif self.parser_type == "parsernaam":
                results = self.parse_with_parsernaam([name])
                return results[0] if results else ParsedName(original=name, confidence=0.0)
            else:  # auto
                # Use parsernaam for Indian names, humanname otherwise
                if HAS_PARSERNAAM and self.is_indian_name(name):
                    results = self.parse_with_parsernaam([name])
                    return results[0] if results else self.parse_with_humanname(name)
                else:
                    return self.parse_with_humanname(name)
        
        # Handle list of names
        names_list = name if isinstance(name, list) else [name]
        
        if self.parser_type == "humanname":
            return [self.parse_with_humanname(n) for n in names_list]
        elif self.parser_type == "parsernaam":
            return self.parse_with_parsernaam(names_list)
        else:  # auto
            # Separate Indian and non-Indian names
            indian_names = []
            indian_indices = []
            regular_names = []
            regular_indices = []
            
            for i, n in enumerate(names_list):
                if HAS_PARSERNAAM and self.is_indian_name(n):
                    indian_names.append(n)
                    indian_indices.append(i)
                else:
                    regular_names.append(n)
                    regular_indices.append(i)
            
            # Parse each group
            results = [None] * len(names_list)
            
            # Parse Indian names with parsernaam
            if indian_names:
                parsed_indian = self.parse_with_parsernaam(indian_names)
                for i, idx in enumerate(indian_indices):
                    results[idx] = parsed_indian[i]
            
            # Parse regular names with humanname
            for i, idx in enumerate(regular_indices):
                results[idx] = self.parse_with_humanname(regular_names[i])
            
            return results
    
    def parse_dataframe(
        self, 
        df: pd.DataFrame, 
        name_column: str = "name",
        add_components: bool = True
    ) -> pd.DataFrame:
        """Parse names in a DataFrame.
        
        Args:
            df: Input DataFrame
            name_column: Column containing names
            add_components: Whether to add parsed components as new columns
            
        Returns:
            DataFrame with parsed names
        """
        if name_column not in df.columns:
            raise ValueError(f"Column '{name_column}' not found in DataFrame")
        
        names = df[name_column].tolist()
        parsed = self.parse(names)
        
        if add_components:
            # Add parsed components as new columns
            df['parsed_first_name'] = [p.first_name for p in parsed]
            df['parsed_middle_name'] = [p.middle_name for p in parsed]
            df['parsed_last_name'] = [p.last_name for p in parsed]
            df['parsed_title'] = [p.title for p in parsed]
            df['parsed_suffix'] = [p.suffix for p in parsed]
            df['parsed_confidence'] = [p.confidence for p in parsed]
            df['parser_used'] = [p.parser_used for p in parsed]
        else:
            # Just add the parsed name objects
            df['parsed_name'] = parsed
        
        return df


def parse_names(
    names: Union[str, List[str], pd.DataFrame],
    parser_type: str = "auto",
    name_column: Optional[str] = "name"
) -> Union[ParsedName, List[ParsedName], pd.DataFrame]:
    """Convenience function to parse names.
    
    Args:
        names: Single name, list of names, or DataFrame
        parser_type: "humanname", "parsernaam", or "auto"
        name_column: Column name if input is DataFrame
        
    Returns:
        Parsed results in same format as input
    """
    parser = NameParser(parser_type=parser_type)
    
    if isinstance(names, pd.DataFrame):
        return parser.parse_dataframe(names, name_column=name_column)
    else:
        return parser.parse(names)


def compare_parsers(name: str) -> Dict[str, ParsedName]:
    """Compare results from different parsers.
    
    Args:
        name: Name to parse
        
    Returns:
        Dictionary with results from each parser
    """
    results = {}
    
    # Parse with HumanName
    hn_parser = NameParser(parser_type="humanname")
    results['humanname'] = hn_parser.parse(name)
    
    # Parse with parsernaam if available
    if HAS_PARSERNAAM:
        pn_parser = NameParser(parser_type="parsernaam")
        results['parsernaam'] = pn_parser.parse(name)
    
    # Parse with auto
    auto_parser = NameParser(parser_type="auto")
    results['auto'] = auto_parser.parse(name)
    
    return results