"""
Question management API routes with multi-market support.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.database.models import Question, QuestionStatus, QuestionUpdate
from backend.database.supabase_client import SupabaseClient
from backend.api.dependencies import get_db_client
from backend.config.markets import get_all_markets, get_market_config
from backend.utils.logger import log


router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/", response_model=List[Question])
async def get_questions(
    status: Optional[QuestionStatus] = None,
    market: Optional[str] = Query(default=None, description="Filter by market segment"),
    platform: Optional[str] = Query(default=None, description="Filter by platform"),
    min_score: Optional[float] = Query(default=None, description="Minimum confidence score"),
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: SupabaseClient = Depends(get_db_client)
):
    """
    Get questions with optional filtering by market, status, platform, etc.
    
    Args:
        status: Filter by status
        market: Filter by market segment (indie_authors, course_creators, etc.)
        platform: Filter by platform (reddit, quora, etc.)
        min_score: Minimum confidence score filter
        limit: Maximum number of questions to return
        offset: Offset for pagination
        db: Database client
        
    Returns:
        List of questions
    """
    try:
        questions = await db.get_questions(
            status=status,
            market=market,
            platform=platform,
            min_score=min_score,
            limit=limit,
            offset=offset
        )
        
        return questions
        
    except Exception as e:
        log.error(f"Error fetching questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{question_id}", response_model=Question)
async def get_question(
    question_id: UUID,
    db: SupabaseClient = Depends(get_db_client)
):
    """
    Get a specific question by ID.
    
    Args:
        question_id: Question UUID
        db: Database client
        
    Returns:
        Question object
    """
    try:
        question = await db.get_question(question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return question
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{question_id}", response_model=dict)
async def update_question(
    question_id: UUID,
    update: QuestionUpdate,
    db: SupabaseClient = Depends(get_db_client)
):
    """
    Update a question.
    
    Args:
        question_id: Question UUID
        update: Update fields
        db: Database client
        
    Returns:
        Success message
    """
    try:
        # Verify question exists
        question = await db.get_question(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Update status if provided
        if update.status:
            success = await db.update_question_status(question_id, update.status)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update question")
        
        return {"message": "Question updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{question_id}/comments")
async def get_question_comments(
    question_id: UUID,
    db: SupabaseClient = Depends(get_db_client)
):
    """
    Get comments for a question.
    
    Args:
        question_id: Question UUID
        db: Database client
        
    Returns:
        List of comments
    """
    try:
        comments = await db.get_comments_for_question(question_id)
        return comments
        
    except Exception as e:
        log.error(f"Error fetching comments for question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/markets/list")
async def get_markets():
    """
    Get list of all available market segments.
    
    Returns:
        List of market configurations
    """
    try:
        markets = get_all_markets()
        market_details = []
        
        for market_name in markets:
            config = get_market_config(market_name)
            if config:
                market_details.append({
                    "name": config.name,
                    "description": config.description,
                    "platforms": config.platforms,
                    "crawl_interval_hours": config.crawl_interval_hours
                })
        
        return market_details
        
    except Exception as e:
        log.error(f"Error fetching markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

