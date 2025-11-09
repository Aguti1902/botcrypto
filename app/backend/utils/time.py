"""Time utilities for consistent timestamp handling."""
from datetime import datetime, timezone
from typing import Union


def now_utc() -> datetime:
    """Get current UTC time.
    
    Returns:
        Current UTC datetime with timezone info
    """
    return datetime.now(timezone.utc)


def to_timestamp(dt: datetime) -> int:
    """Convert datetime to Unix timestamp in milliseconds.
    
    Args:
        dt: Datetime to convert
        
    Returns:
        Unix timestamp in milliseconds
    """
    return int(dt.timestamp() * 1000)


def from_timestamp(timestamp: Union[int, float]) -> datetime:
    """Convert Unix timestamp to datetime.
    
    Args:
        timestamp: Unix timestamp in milliseconds or seconds
        
    Returns:
        UTC datetime with timezone info
    """
    # Auto-detect if timestamp is in seconds or milliseconds
    if timestamp > 10**10:  # Likely milliseconds
        timestamp = timestamp / 1000
    
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def to_iso(dt: datetime) -> str:
    """Convert datetime to ISO 8601 string.
    
    Args:
        dt: Datetime to convert
        
    Returns:
        ISO 8601 string
    """
    return dt.isoformat()


def from_iso(iso_string: str) -> datetime:
    """Convert ISO 8601 string to datetime.
    
    Args:
        iso_string: ISO 8601 string
        
    Returns:
        UTC datetime with timezone info
    """
    dt = datetime.fromisoformat(iso_string)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

