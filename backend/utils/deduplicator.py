"""
Deduplication logic to prevent processing duplicate questions.
"""
import hashlib
from typing import Optional
from backend.utils.logger import log


class Deduplicator:
    """Handle duplicate detection for questions."""
    
    @staticmethod
    def generate_content_hash(content: str) -> str:
        """
        Generate a hash from question content for deduplication.
        
        Args:
            content: Question text to hash
            
        Returns:
            SHA256 hash of normalized content
        """
        # Normalize content: lowercase, strip whitespace
        normalized = content.lower().strip()
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    @staticmethod
    def is_similar(text1: str, text2: str, threshold: float = 0.8) -> bool:
        """
        Check if two texts are similar using simple ratio.
        
        Args:
            text1: First text
            text2: Second text
            threshold: Similarity threshold (0-1)
            
        Returns:
            True if texts are similar
        """
        # Simple character-based similarity
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        if text1_lower == text2_lower:
            return True
        
        # Calculate character overlap
        set1 = set(text1_lower.split())
        set2 = set(text2_lower.split())
        
        if not set1 or not set2:
            return False
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        similarity = intersection / union if union > 0 else 0
        
        return similarity >= threshold
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize URL for comparison.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        # Remove common URL parameters
        url = url.split('?')[0]
        url = url.split('#')[0]
        # Remove trailing slash
        url = url.rstrip('/')
        
        return url.lower()
    
    @staticmethod
    def extract_platform_id(url: str, platform: str) -> Optional[str]:
        """
        Extract post ID from platform URL.
        
        Args:
            url: Platform URL
            platform: Platform name (reddit, quora)
            
        Returns:
            Post ID or None
        """
        try:
            if platform == "reddit":
                # Reddit URL format: .../comments/POST_ID/...
                parts = url.split('/')
                if 'comments' in parts:
                    idx = parts.index('comments')
                    if idx + 1 < len(parts):
                        return parts[idx + 1]
            
            elif platform == "quora":
                # Quora URL format: .../QUESTION-ID/...
                parts = url.split('/')
                # Last meaningful part is usually the ID
                for part in reversed(parts):
                    if part and part not in ['', 'answer']:
                        return part
            
            return None
            
        except Exception as e:
            log.error(f"Error extracting platform ID: {e}")
            return None

