"""
Celery tasks for crawling social media platforms.
"""
from celery import shared_task
from backend.crawler.crawler_manager import crawler_manager
from backend.utils.logger import log


@shared_task(name="backend.tasks.crawl_tasks.crawl_platform")
def crawl_platform_task(platform: str, limit: int = 100):
    """
    Celery task to crawl a specific platform.
    
    Args:
        platform: Platform name (reddit, quora)
        limit: Maximum questions to fetch
        
    Returns:
        Crawl results dictionary
    """
    try:
        log.info(f"Starting Celery task: crawl {platform}")
        
        # Note: Celery tasks can't be async by default, so we use sync wrapper
        import asyncio
        result = asyncio.run(crawler_manager.crawl_platform(platform, limit))
        
        log.info(f"Completed crawl task for {platform}: {result}")
        
        return result
        
    except Exception as e:
        log.error(f"Error in crawl task for {platform}: {e}")
        return {"error": str(e), "platform": platform}


@shared_task(name="backend.tasks.crawl_tasks.scheduled_crawl_all")
def scheduled_crawl_all(limit: int = 100):
    """
    Scheduled task to crawl all platforms.
    
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


@shared_task(name="backend.tasks.crawl_tasks.crawl_reddit")
def crawl_reddit_task(limit: int = 100):
    """
    Task to crawl Reddit.
    
    Args:
        limit: Maximum questions to fetch
        
    Returns:
        Crawl results
    """
    return crawl_platform_task("reddit", limit)


@shared_task(name="backend.tasks.crawl_tasks.crawl_quora")
def crawl_quora_task(limit: int = 100):
    """
    Task to crawl Quora.
    
    Args:
        limit: Maximum questions to fetch
        
    Returns:
        Crawl results
    """
    return crawl_platform_task("quora", limit)

