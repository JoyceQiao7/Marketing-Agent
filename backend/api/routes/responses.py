"""
Response management API routes.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from backend.database.models import AgentResponse
from backend.database.supabase_client import SupabaseClient
from backend.agent.response_generator import ResponseGenerator
from backend.api.dependencies import get_db_client, get_response_generator
from backend.utils.logger import log


router = APIRouter(prefix="/responses", tags=["responses"])


@router.get("/{question_id}", response_model=AgentResponse)
async def get_response(
    question_id: UUID,
    db: SupabaseClient = Depends(get_db_client)
):
    """
    Get agent response for a question.
    
    Args:
        question_id: Question UUID
        db: Database client
        
    Returns:
        Agent response
    """
    try:
        response = await db.get_agent_response(question_id)
        
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching response for question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{question_id}/generate")
async def generate_response(
    question_id: UUID,
    generator: ResponseGenerator = Depends(get_response_generator),
    db: SupabaseClient = Depends(get_db_client)
):
    """
    Generate a response for a question.
    
    Args:
        question_id: Question UUID
        generator: Response generator
        db: Database client
        
    Returns:
        Generated response
    """
    try:
        # Get question
        question = await db.get_question(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Get agent response
        agent_response = await db.get_agent_response(question_id)
        if not agent_response:
            raise HTTPException(status_code=404, detail="Agent response not found. Run capability check first.")
        
        # Generate response
        response_text = await generator.generate_response(question, agent_response)
        
        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to generate response")
        
        return {
            "question_id": question_id,
            "response_text": response_text
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error generating response for question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{question_id}/post")
async def post_response(
    question_id: UUID,
    generator: ResponseGenerator = Depends(get_response_generator),
    db: SupabaseClient = Depends(get_db_client)
):
    """
    Post a response to a platform.
    
    Args:
        question_id: Question UUID
        generator: Response generator
        db: Database client
        
    Returns:
        Success message
    """
    try:
        # Process question (generate and post)
        success = await generator.process_question(question_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process question")
        
        return {
            "message": "Response posted successfully",
            "question_id": question_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error posting response for question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

