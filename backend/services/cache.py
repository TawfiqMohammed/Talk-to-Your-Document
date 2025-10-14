"""
Cache Service for managing embeddings cache
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict
from backend.config import CACHE_DIR

class CacheService:
    """Service for caching embeddings"""
    
    @staticmethod
    def get_cache_path(doc_id: str) -> str:
        """Get cache file path for document"""
        return os.path.join(CACHE_DIR, f"{doc_id}_embeddings.json")
    
    @staticmethod
    def check_cache(doc_id: str) -> bool:
        """
        Check if embeddings are cached
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if cache exists
        """
        cache_file = CacheService.get_cache_path(doc_id)
        return os.path.exists(cache_file)
    
    @staticmethod
    def save_cache(doc_id: str, chunks_count: int) -> bool:
        """
        Save cache metadata
        
        Args:
            doc_id: Document identifier
            chunks_count: Number of chunks embedded
            
        Returns:
            Success boolean
        """
        try:
            cache_file = CacheService.get_cache_path(doc_id)
            cache_data = {
                "doc_id": doc_id,
                "timestamp": datetime.now().isoformat(),
                "chunks_count": chunks_count
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"💾 Cached embeddings for {doc_id}")
            return True
            
        except Exception as e:
            print(f"❌ Cache save failed: {str(e)}")
            return False
    
    @staticmethod
    def load_cache(doc_id: str) -> Optional[Dict]:
        """
        Load cache metadata
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Cache data dictionary or None
        """
        try:
            cache_file = CacheService.get_cache_path(doc_id)
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"❌ Cache load failed: {str(e)}")
            return None
    
    @staticmethod
    def delete_cache(doc_id: str) -> bool:
        """
        Delete cache file
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Success boolean
        """
        try:
            cache_file = CacheService.get_cache_path(doc_id)
            
            if os.path.exists(cache_file):
                os.remove(cache_file)
                print(f"🗑️  Deleted cache for {doc_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Cache deletion failed: {str(e)}")
            return False