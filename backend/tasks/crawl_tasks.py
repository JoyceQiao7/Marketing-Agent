"""
Celery tasks for crawling social media platforms with multi-market support.
"""
from celery import shared_task
from backend.crawler.crawler_manager import crawler_manager
from backend.utils.logger import log


@shared_task(name="backend.tasks.crawl_tasks.crawl_platform")
def crawl_platform_task(platform: str, market: str = None, limit: int = 100):
    """
    Celery task to crawl a specific platform for a specific market.
    
    Args:
        platform: Platform name (reddit, quora)
        market: Market segment name (optional)
        limit: Maximum questions to fetch
        
    Returns:
        Crawl results dictionary
    """
    try:
        log.info(f"Starting Celery task: crawl {platform}" + 
                (f" for market '{market}'" if market else ""))
        
        # Note: Celery tasks can't be async by default, so we use sync wrapper
        import asyncio
        result = asyncio.run(crawler_manager.crawl_platform(platform, market, limit))
        
        log.info(f"Completed crawl task for {platform}" + 
                (f" (market: {market})" if market else "") + f": {result}")
        
        return result
        
    except Exception as e:
        log.error(f"Error in crawl task for {platform}" + 
                 (f" (market: {market})" if market else "") + f": {e}")
        return {"error": str(e), "platform": platform, "market": market}


@shared_task(name="backend.tasks.crawl_tasks.crawl_market_task")
def crawl_market_task(market: str, limit: int = 100):
    """
    Celery task to crawl all platforms for a specific market.
    
    Args:
        market: Market segment name (indie_authors, course_creators, etc.)
        limit: Maximum questions per platform
        
    Returns:
        Market crawl results dictionary
    """
    try:
        log.info(f"Starting Celery task: crawl market '{market}'")
        
        import asyncio
        result = asyncio.run(crawler_manager.crawl_market(market, limit))
        
        log.info(f"Completed crawl task for market '{market}': {result}")
        
        return result
        
    except Exception as e:
        log.error(f"Error in crawl task for market '{market}': {e}")
        return {"error": str(e), "market": market}


@shared_task(name="backend.tasks.crawl_tasks.scheduled_crawl_all")
def scheduled_crawl_all(limit: int = 100):
    """
    Scheduled task to crawl all platforms (backwards compatible).
    
    Args:
        limit: Maximum questions per platform
        
    Returns:
        List of crawl results
    """
    try:
        log.info("Starting scheduled crawl for all platforms")
        
        import asyncio
        results = asyncio.run(crawler_manager.crawl_all_platforms(limit))
        
        log.info(f"Completed scheduled crawl for all platforms")
        
        return results
        
    except Exception as e:
        log.error(f"Error in scheduled crawl: {e}")
        return [{"error": str(e)}]


@shared_task(name="backend.tasks.crawl_tasks.scheduled_crawl_all_markets")
def scheduled_crawl_all_markets(limit: int = 100):
    """
    Scheduled task to crawl all configured markets.
    
    Args:
        limit: Maximum questions per platform per market
        
    Returns:
        List of market crawl results
    """
    try:
        log.info("Starting scheduled crawl for all markets")
        
        import asyncio
        results = asyncio.run(crawler_manager.crawl_all_markets(limit))
        
        log.info(f"Completed scheduled crawl for all markets")
        
        return results
        
    except Exception as e:
        log.error(f"Error in scheduled market crawl: {e}")
        return [{"error": str(e)}]


@shared_task(name="backend.tasks.crawl_tasks.crawl_reddit")
def crawl_reddit_task(market: str = None, limit: int = 100):
    """
    Task to crawl Reddit for a specific market.
    
    Args:
        market: Market segment name (optional)
        limit: Maximum questions to fetch
        
    Returns:
        Crawl results
    """
    return crawl_platform_task("reddit", market, limit)


@shared_task(name="backend.tasks.crawl_tasks.crawl_quora")
def crawl_quora_task(market: str = None, limit: int = 100):
    """
    Task to crawl Quora for a specific market.
    
    Args:
        market: Market segment name (optional)
        limit: Maximum questions to fetch
        
    Returns:
        Crawl results
    """
    return crawl_platform_task("quora", market, limit)
