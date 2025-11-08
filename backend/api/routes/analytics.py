"""
Analytics and statistics API routes.
"""
from fastapi import APIRouter, Depends
from backend.database.models import AnalyticsResponse
from backend.database.supabase_client import SupabaseClient
from backend.api.dependencies import get_db_client
from backend.utils.logger import log


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    db: SupabaseClient = Depends(get_db_client)
):
    """
    Get overall analytics and statistics.
    
    Args:
        db: Database client
        
    Returns:
        Analytics summary
    """
    try:
        # Get question counts
        questions_by_status = await db.get_question_count_by_status()
        questions_by_platform = await db.get_question_count_by_platform()
        
        # Get response stats
        response_stats = await db.get_response_stats()
        
        # Calculate totals
        total_questions = sum(questions_by_status.values())
        
        return AnalyticsResponse(
            total_questions=total_questions,
            questions_by_status=questions_by_status,
            questions_by_platform=questions_by_platform,
            total_responses=response_stats['total'],
            response_success_rate=response_stats['success_rate'],
            avg_confidence_score=response_stats['avg_confidence']
        )
        
    except Exception as e:
        log.error(f"Error fetching analytics: {e}")
        return AnalyticsResponse(
            total_questions=0,
            questions_by_status={},
            questions_by_platform={},
            total_responses=0,
            response_success_rate=0.0,
            avg_confidence_score=0.0
        )


@router.get("/crawl-logs")
async def get_crawl_logs(
    limit: int = 10,
    db: SupabaseClient = Depends(get_db_client)
):
    """
    Get recent crawl logs.
    
    Args:
        limit: Maximum number of logs to return
        db: Database client
        
    Returns:
        List of crawl logs
    """
    try:
        logs = await db.get_recent_crawl_logs(limit)
        return logs
        
    except Exception as e:
        log.error(f"Error fetching crawl logs: {e}")
        return []

