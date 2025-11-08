"""
Crawler manager to orchestrate all platform crawlers.
"""
from typing import List, Dict
from datetime import datetime
from backend.crawler.reddit_crawler import RedditCrawler
from backend.crawler.quora_crawler import QuoraCrawler
from backend.database.models import QuestionCreate, CrawlLog, CrawlStatus, PlatformEnum
from backend.database.supabase_client import db_client
from backend.utils.logger import log
from backend.utils.deduplicator import Deduplicator


class CrawlerManager:
    """Manage and coordinate all platform crawlers."""
    
    def __init__(self):
        """Initialize crawler manager with all platform crawlers."""
        self.crawlers = {
            "reddit": RedditCrawler(),
            "quora": QuoraCrawler()
        }
        self.deduplicator = Deduplicator()
        log.info("Crawler manager initialized")
    
    async def crawl_platform(self, platform: str, limit: int = 100) -> Dict[str, any]:
        """
        Crawl a specific platform.
        
        Args:
            platform: Platform name (reddit, quora)
            limit: Maximum questions to fetch
            
        Returns:
            Dictionary with crawl results
        """
        if platform not in self.crawlers:
            log.error(f"Unknown platform: {platform}")
            return {"error": f"Unknown platform: {platform}"}
        
        crawler = self.crawlers[platform]
        started_at = datetime.utcnow()
        
        # Create crawl log
        log_entry = CrawlLog(
            platform=platform,
            status=CrawlStatus.SUCCESS,
            items_found=0,
            items_stored=0,
            started_at=started_at
        )
        
        try:
            # Fetch questions
            log.info(f"Starting crawl for {platform}")
            questions = await crawler.crawl(limit)
            
            log_entry.items_found = len(questions)
            
            # Store questions in database
            stored_count = 0
            duplicate_count = 0
            
            for question in questions:
                # Check for duplicates
                exists = await db_client.check_question_exists(
                    question.platform.value,
                    question.post_id
                )
                
                if exists:
                    duplicate_count += 1
                    log.debug(f"Duplicate question found: {question.post_id}")
                    continue
                
                # Generate and check content hash
                content_hash = self.deduplicator.generate_content_hash(question.content)
                hash_exists = await db_client.check_content_hash_exists(content_hash)
                
                if hash_exists:
                    duplicate_count += 1
                    log.debug(f"Duplicate content found: {question.title[:50]}")
                    continue
                
                # Store question
                stored_question = await db_client.create_question(question)
                if stored_question:
                    stored_count += 1
            
            log_entry.items_stored = stored_count
            log_entry.completed_at = datetime.utcnow()
            
            # Save crawl log
            await db_client.create_crawl_log(log_entry)
            
            log.info(f"Crawl complete for {platform}: {stored_count} stored, {duplicate_count} duplicates")
            
            return {
                "platform": platform,
                "items_found": len(questions),
                "items_stored": stored_count,
                "duplicates": duplicate_count,
                "duration_seconds": (log_entry.completed_at - started_at).total_seconds()
            }
            
        except Exception as e:
            log.error(f"Error crawling {platform}: {e}")
            
            log_entry.status = CrawlStatus.FAILURE
            log_entry.error_message = str(e)
            log_entry.completed_at = datetime.utcnow()
            
            await db_client.create_crawl_log(log_entry)
            
            return {
                "platform": platform,
                "error": str(e)
            }
    
    async def crawl_all_platforms(self, limit: int = 100) -> List[Dict[str, any]]:
        """
        Crawl all configured platforms.
        
        Args:
            limit: Maximum questions to fetch per platform
            
        Returns:
            List of crawl results
        """
        results = []
        
        for platform in self.crawlers.keys():
            result = await self.crawl_platform(platform, limit)
            results.append(result)
        
        return results
    
    def get_crawler(self, platform: str):
        """
        Get crawler for specific platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Crawler instance or None
        """
        return self.crawlers.get(platform)


# Global instance
crawler_manager = CrawlerManager()

