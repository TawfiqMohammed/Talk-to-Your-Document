"""
Helper utilities
"""
import hashlib
import time
from datetime import datetime

def generate_doc_id(filename: str) -> str:
    """
    Generate unique document ID
    
    Args:
        filename: Original filename
        
    Returns:
        Unique 12-character ID
    """
    timestamp = str(time.time())
    return hashlib.md5(f"{filename}{timestamp}".encode()).hexdigest()[:12]

def get_timestamp() -> str:
    """
    Get current timestamp in ISO format
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()

def validate_file_type(content_type: str, allowed_types: list) -> bool:
    """
    Validate file MIME type
    
    Args:
        content_type: File MIME type
        allowed_types: List of allowed types
        
    Returns:
        True if valid
    """
    return content_type in allowed_types

def get_file_extension(filename: str) -> str:
    """
    Get file extension
    
    Args:
        filename: File name
        
    Returns:
        File extension (e.g., 'pdf', 'png')
    """
    return filename.split('.')[-1].lower() if '.' in filename else ''