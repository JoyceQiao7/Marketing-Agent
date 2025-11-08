"""
Crawl management API routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from backend.database.models import CrawlTriggerRequest
from backend.crawler.crawler_manager import CrawlerManager
from backend.api.dependencies import get_crawler_manager
from backend.utils.logger import log


router = APIRouter(prefix="/crawl", tags=["crawl"])


@router.post("/trigger")
async def trigger_crawl(
    request: CrawlTriggerRequest,
    manager: CrawlerManager = Depends(get_crawler_manager)
):
    """
    Manually trigger a crawl for a specific platform.
    
    Args:
        request: Crawl trigger request
        manager: Crawler manager
        
    Returns:
        Crawl results
    """
    try:
        log.info(f"Manual crawl triggered for {request.platform}")
        
        result = await manager.crawl_platform(
            request.platform.value,
            limit=request.limit or 100
        )
        
        return result
        
    except Exception as e:
        log.error(f"Error triggering crawl: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-all")
async def trigger_all_crawls(
    limit: int = 100,
    manager: CrawlerManager = Depends(get_crawler_manager)
):
    """
    Manually trigger crawls for all platforms.
    
    Args:
        limit: Maximum questions per platform
        manager: Crawler manager
        
    Returns:
        List of crawl results
    """
    try:
        log.info("Manual crawl triggered for all platforms")
        
        results = await manager.crawl_all_platforms(limit)
        
        return results
        
    except Exception as e:
        log.error(f"Error triggering crawls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reddit")
async def trigger_reddit_crawl(
    limit: int = 100,
    manager: CrawlerManager = Depends(get_crawler_manager)
):
    """
    Manually trigger Reddit crawl.
    
    Args:
        limit: Maximum questions to fetch
        manager: Crawler manager
        
    Returns:
        Crawl results
    """
    try:
        result = await manager.crawl_platform("reddit", limit)
        return result
        
    except Exception as e:
        log.error(f"Error crawling Reddit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quora")
async def trigger_quora_crawl(
    limit: int = 100,
    manager: CrawlerManager = Depends(get_crawler_manager)
):
    """
    Manually trigger Quora crawl.
    
    Args:
        limit: Maximum questions to fetch
        manager: Crawler manager
        
    Returns:
        Crawl results
    """
    try:
        result = await manager.crawl_platform("quora", limit)
        return result
        
    except Exception as e:
        log.error(f"Error crawling Quora: {e}")
        raise HTTPException(status_code=500, detail=str(e))

