"""
Abstract base crawler class for platform-specific implementations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from backend.database.models import QuestionCreate, Comment
from backend.utils.logger import log
from backend.utils.rate_limiter import get_rate_limiter
from backend.utils.deduplicator import Deduplicator


class BaseCrawler(ABC):
    """Abstract base class for platform crawlers."""
    
    def __init__(self, platform_name: str):
        """
        Initialize crawler.
        
        Args:
            platform_name: Name of the platform (e.g., 'reddit', 'quora')
        """
        self.platform_name = platform_name
        self.rate_limiter = get_rate_limiter()
        self.deduplicator = Deduplicator()
        log.info(f"Initialized {platform_name} crawler")
    
    @abstractmethod
    async def fetch_questions(self, limit: int = 100) -> List[QuestionCreate]:
        """
        Fetch questions from the platform.
        
        Args:
            limit: Maximum number of questions to fetch
            
        Returns:
            List of QuestionCreate objects
        """
        pass
    
    @abstractmethod
    async def fetch_comments(self, question_url: str) -> List[Comment]:
        """
        Fetch comments for a specific question.
        
        Args:
            question_url: URL of the question
            
        Returns:
            List of Comment objects
        """
        pass
    
    @abstractmethod
    async def post_response(self, question_url: str, response_text: str) -> bool:
        """
        Post a response to a question.
        
        Args:
            question_url: URL of the question
            response_text: Response text to post
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def _wait_for_rate_limit(self):
        """Wait if rate limit is reached."""
        self.rate_limiter.wait_if_needed(self.platform_name)
    
    def _normalize_question_data(self, raw_data: Dict[str, Any]) -> QuestionCreate:
        """
        Normalize raw question data to QuestionCreate model.
        
        Args:
            raw_data: Raw question data from platform
            
        Returns:
            QuestionCreate object
        """
        # This should be implemented by subclasses with platform-specific logic
        raise NotImplementedError("Subclass must implement _normalize_question_data")
    
    async def crawl(self, limit: int = 100) -> List[QuestionCreate]:
        """
        Main crawl method with error handling and logging.
        
        Args:
            limit: Maximum number of questions to fetch
            
        Returns:
            List of questions
        """
        try:
            log.info(f"Starting crawl for {self.platform_name}, limit: {limit}")
            questions = await self.fetch_questions(limit)
            log.info(f"Crawled {len(questions)} questions from {self.platform_name}")
            return questions
            
        except Exception as e:
            log.error(f"Error crawling {self.platform_name}: {e}")
            return []

