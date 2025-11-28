"""
Crawl management API routes with multi-market support.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.database.models import CrawlTriggerRequest
from backend.crawler.crawler_manager import CrawlerManager
from backend.api.dependencies import get_crawler_manager
from backend.utils.logger import log


router = APIRouter(prefix="/crawl", tags=["crawl"])


@router.post("/trigger")
async def trigger_crawl(
    request: CrawlTriggerRequest,
    market: Optional[str] = Query(default=None, description="Market segment to crawl"),
    manager: CrawlerManager = Depends(get_crawler_manager)
):
    """
    Manually trigger a crawl for a specific platform and optional market.
    
    Args:
        request: Crawl trigger request
        market: Optional market segment filter
        manager: Crawler manager
        
    Returns:
        Crawl results
    """
    try:
        log.info(f"Manual crawl triggered for {request.platform}" + 
                (f" (market: {market})" if market else ""))
        
        result = await manager.crawl_platform(
            request.platform.value,
            market=market,
            limit=request.limit or 100
        )
        
        return result
        
    except Exception as e:
        log.error(f"Error triggering crawl: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/market/{market_name}")
async def trigger_market_crawl(
    market_name: str,
    limit: int = Query(default=100, description="Maximum questions to fetch"),
    manager: CrawlerManager = Depends(get_crawler_manager)
):
    """
    Manually trigger crawl for all platforms in a specific market.
    
    Args:
        market_name: Market segment name (e.g., indie_authors, course_creators)
        limit: Maximum questions per platform
        manager: Crawler manager
        
    Returns:
        Market crawl results
    """
    try:
        log.info(f"Manual market crawl triggered for '{market_name}'")
        
        result = await manager.crawl_market(market_name, limit)
        
        return result
        
    except Exception as e:
        log.error(f"Error triggering market crawl: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-all")
async def trigger_all_crawls(
    limit: int = 100,
    manager: CrawlerManager = Depends(get_crawler_manager)
):
    """
    Manually trigger crawls for all platforms (backwards compatible).
    
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


@router.post("/trigger-all-markets")
async def trigger_all_markets_crawl(
    limit: int = Query(default=100, description="Maximum questions per platform per market"),
    manager: CrawlerManager = Depends(get_crawler_manager)
):
    """
    Manually trigger crawls for all configured markets.
    
    Args:
        limit: Maximum questions per platform per market
        manager: Crawler manager
        
    Returns:
        List of market crawl results
    """
    try:
        log.info("Manual crawl triggered for all markets")
        
        results = await manager.crawl_all_markets(limit)
        
        return results
        
    except Exception as e:
        log.error(f"Error triggering market crawls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reddit")
async def trigger_reddit_crawl(
    limit: int = 100,
    market: Optional[str] = Query(default=None, description="Market segment to crawl"),
    manager: CrawlerManager = Depends(get_crawler_manager)
):
    """
    Manually trigger Reddit crawl.
    
    Args:
        limit: Maximum questions to fetch
        market: Optional market segment filter
        manager: Crawler manager
        
    Returns:
        Crawl results
    """
    try:
        result = await manager.crawl_platform("reddit", market=market, limit=limit)
        return result
        
    except Exception as e:
        log.error(f"Error crawling Reddit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quora")
async def trigger_quora_crawl(
    limit: int = 100,
    market: Optional[str] = Query(default=None, description="Market segment to crawl"),
    manager: CrawlerManager = Depends(get_crawler_manager)
):
    """
    Manually trigger Quora crawl.
    
    Args:
        limit: Maximum questions to fetch
        market: Optional market segment filter
        manager: Crawler manager
        
    Returns:
        Crawl results
    """
    try:
        result = await manager.crawl_platform("quora", market=market, limit=limit)
        return result
        
    except Exception as e:
        log.error(f"Error crawling Quora: {e}")
        raise HTTPException(status_code=500, detail=str(e))
