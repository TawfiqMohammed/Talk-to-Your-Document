"""
Text chunking utilities
"""
from typing import List
from backend.config import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Input text to chunk
        chunk_size: Number of words per chunk
        overlap: Number of overlapping words between chunks
        
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk.strip())
    
    return chunks

def calculate_stats(text: str) -> dict:
    """
    Calculate text statistics
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with word count, char count, estimated reading time
    """
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    reading_time = max(1, word_count // 200)  # ~200 words per minute
    
    return {
        "word_count": word_count,
        "char_count": char_count,
        "reading_time": reading_time
    }