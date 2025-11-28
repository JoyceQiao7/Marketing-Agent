"""
Crawler manager to orchestrate all platform crawlers with multi-market support.
"""
from typing import List, Dict, Optional
from datetime import datetime
from backend.crawler.reddit_crawler import RedditCrawler
from backend.crawler.quora_crawler import QuoraCrawler
from backend.database.models import QuestionCreate, CrawlLog, CrawlStatus, PlatformEnum
from backend.database.supabase_client import db_client
from backend.config.markets import get_market_config, get_all_markets
from backend.utils.logger import log
from backend.utils.deduplicator import Deduplicator


class CrawlerManager:
    """Manage and coordinate all platform crawlers with market segmentation."""
    
    def __init__(self):
        """Initialize crawler manager."""
        self.deduplicator = Deduplicator()
        log.info("Crawler manager initialized")
    
    def get_crawler(self, platform: str, market: Optional[str] = None):
        """
        Get crawler instance for specific platform and market.
        
        Args:
            platform: Platform name (reddit, quora, etc.)
            market: Market segment name
            
        Returns:
            Crawler instance or None
        """
        if platform == "reddit":
            return RedditCrawler(market_name=market)
        elif platform == "quora":
            return QuoraCrawler(market_name=market)
        else:
            log.error(f"Unknown platform: {platform}")
            return None
    
    async def crawl_market(self, market: str, limit: int = 100) -> Dict[str, any]:
        """
        Crawl all platforms for a specific market.
        
        Args:
            market: Market segment name
            limit: Maximum questions to fetch per platform
            
        Returns:
            Dictionary with crawl results
        """
        market_config = get_market_config(market)
        if not market_config:
            log.error(f"Unknown market: {market}")
            return {"error": f"Unknown market: {market}"}
        
        log.info(f"Starting market crawl for '{market}' across {len(market_config.platforms)} platforms")
        
        results = []
        total_stored = 0
        total_found = 0
        
        for platform in market_config.platforms:
            result = await self.crawl_platform(platform, market, limit)
            results.append(result)
            
            if 'items_stored' in result:
                total_stored += result['items_stored']
            if 'items_found' in result:
                total_found += result['items_found']
        
        log.info(f"Market crawl complete for '{market}': {total_stored} stored from {total_found} found")
        
        return {
            "market": market,
            "total_found": total_found,
            "total_stored": total_stored,
            "platforms": results
        }
    
    async def crawl_platform(self, platform: str, market: Optional[str] = None, limit: int = 100) -> Dict[str, any]:
        """
        Crawl a specific platform for a specific market.
        
        Args:
            platform: Platform name (reddit, quora)
            market: Market segment name (optional)
            limit: Maximum questions to fetch
            
        Returns:
            Dictionary with crawl results
        """
        crawler = self.get_crawler(platform, market)
        if not crawler:
            return {"error": f"Unknown platform: {platform}"}
        
        started_at = datetime.utcnow()
        
        # Create crawl log
        log_entry = CrawlLog(
            platform=platform,
            market=market,
            status=CrawlStatus.SUCCESS,
            items_found=0,
            items_stored=0,
            started_at=started_at
        )
        
        try:
            # Fetch questions
            log.info(f"Starting crawl for {platform}" + (f" (market: {market})" if market else ""))
            questions = await crawler.crawl(limit)
            
            log_entry.items_found = len(questions)
            
            # Store questions in database
            stored_count = 0
            duplicate_count = 0
            
            for question in questions:
                # Check for duplicates by post_id
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
            
            log.info(f"Crawl complete for {platform}" + (f" (market: {market})" if market else "") + 
                    f": {stored_count} stored, {duplicate_count} duplicates")
            
            return {
                "platform": platform,
                "market": market,
                "items_found": len(questions),
                "items_stored": stored_count,
                "duplicates": duplicate_count,
                "duration_seconds": (log_entry.completed_at - started_at).total_seconds()
            }
            
        except Exception as e:
            log.error(f"Error crawling {platform}" + (f" (market: {market})" if market else "") + f": {e}")
            
            log_entry.status = CrawlStatus.FAILURE
            log_entry.error_message = str(e)
            log_entry.completed_at = datetime.utcnow()
            
            await db_client.create_crawl_log(log_entry)
            
            return {
                "platform": platform,
                "market": market,
                "error": str(e)
            }
    
    async def crawl_all_markets(self, limit: int = 100) -> List[Dict[str, any]]:
        """
        Crawl all configured markets.
        
        Args:
            limit: Maximum questions to fetch per platform per market
            
        Returns:
            List of crawl results per market
        """
        markets = get_all_markets()
        results = []
        
        for market in markets:
            result = await self.crawl_market(market, limit)
            results.append(result)
        
        return results
    
    async def crawl_all_platforms(self, limit: int = 100) -> List[Dict[str, any]]:
        """
        Crawl all platforms without market filtering (backwards compatibility).
        
        Args:
            limit: Maximum questions to fetch per platform
            
        Returns:
            List of crawl results
        """
        results = []
        platforms = ["reddit", "quora"]
        
        for platform in platforms:
            result = await self.crawl_platform(platform, market=None, limit=limit)
            results.append(result)
        
        return results


# Global instance
crawler_manager = CrawlerManager()
