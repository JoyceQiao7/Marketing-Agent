"""
Celery tasks for processing questions and generating responses.
"""
from uuid import UUID
from celery import shared_task
from backend.database.models import QuestionStatus
from backend.database.supabase_client import db_client
from backend.agent.capability_checker import capability_checker
from backend.agent.response_generator import response_generator
from backend.utils.logger import log


@shared_task(name="backend.tasks.response_tasks.check_question_capability")
def check_question_capability_task(question_id: str):
    """
    Task to check if a question can be answered by Mulan Agent.
    
    Args:
        question_id: Question UUID as string
        
    Returns:
        Agent response dictionary
    """
    try:
        log.info(f"Starting capability check task for question: {question_id}")
        
        import asyncio
        
        # Convert string to UUID
        question_uuid = UUID(question_id)
        
        # Get question
        question = asyncio.run(db_client.get_question(question_uuid))
        
        if not question:
            log.error(f"Question {question_id} not found")
            return {"error": "Question not found"}
        
        # Check capability
        agent_response = asyncio.run(capability_checker.check_question(question))
        
        log.info(f"Capability check complete for question {question_id}: in_scope={agent_response.is_in_scope}")
        
        return {
            "question_id": str(agent_response.question_id),
            "is_in_scope": agent_response.is_in_scope,
            "confidence_score": agent_response.confidence_score
        }
        
    except Exception as e:
        log.error(f"Error in capability check task: {e}")
        return {"error": str(e), "question_id": question_id}


@shared_task(name="backend.tasks.response_tasks.generate_and_post_response")
def generate_and_post_response_task(question_id: str):
    """
    Task to generate and post a response to a question.
    
    Args:
        question_id: Question UUID as string
        
    Returns:
        Result dictionary
    """
    try:
        log.info(f"Starting response generation task for question: {question_id}")
        
        import asyncio
        
        # Convert string to UUID
        question_uuid = UUID(question_id)
        
        # Process question (generate and optionally post)
        success = asyncio.run(response_generator.process_question(question_uuid))
        
        if success:
            log.info(f"Response task complete for question {question_id}")
            return {"success": True, "question_id": question_id}
        else:
            log.error(f"Response task failed for question {question_id}")
            return {"success": False, "question_id": question_id}
        
    except Exception as e:
        log.error(f"Error in response generation task: {e}")
        return {"error": str(e), "question_id": question_id}


@shared_task(name="backend.tasks.response_tasks.process_pending_questions_task")
def process_pending_questions_task(limit: int = 10):
    """
    Scheduled task to process pending questions.
    
    Args:
        limit: Maximum questions to process
        
    Returns:
        Number of questions processed
    """
    try:
        log.info(f"Starting scheduled processing of pending questions (limit: {limit})")
        
        import asyncio
        
        # Get pending questions
        pending_questions = asyncio.run(
            db_client.get_questions_by_status(QuestionStatus.PENDING, limit)
        )
        
        log.info(f"Found {len(pending_questions)} pending questions")
        
        processed_count = 0
        
        for question in pending_questions:
            try:
                # Check if agent response exists
                agent_response = asyncio.run(db_client.get_agent_response(question.id))
                
                if not agent_response:
                    # Run capability check first
                    log.info(f"Running capability check for question {question.id}")
                    agent_response = asyncio.run(capability_checker.check_question(question))
                
                # If in scope, generate and post response
                if agent_response and agent_response.is_in_scope:
                    log.info(f"Processing question {question.id}")
                    success = asyncio.run(response_generator.process_question(question.id))
                    
                    if success:
                        processed_count += 1
                else:
                    # Mark as ignored
                    asyncio.run(db_client.update_question_status(question.id, QuestionStatus.IGNORED))
                    
            except Exception as e:
                log.error(f"Error processing question {question.id}: {e}")
                continue
        
        log.info(f"Processed {processed_count} questions successfully")
        
        return {
            "processed": processed_count,
            "total_pending": len(pending_questions)
        }
        
    except Exception as e:
        log.error(f"Error in process pending questions task: {e}")
        return {"error": str(e)}


@shared_task(name="backend.tasks.response_tasks.batch_check_capabilities")
def batch_check_capabilities_task(question_ids: list):
    """
    Task to batch check capabilities for multiple questions.
    
    Args:
        question_ids: List of question UUID strings
        
    Returns:
        Results dictionary
    """
    try:
        log.info(f"Starting batch capability check for {len(question_ids)} questions")
        
        import asyncio
        
        # Convert strings to UUIDs
        uuids = [UUID(qid) for qid in question_ids]
        
        results = asyncio.run(capability_checker.batch_check_questions(uuids))
        
        log.info(f"Batch capability check complete for {len(results)} questions")
        
        return {
            "total": len(results),
            "in_scope": sum(1 for r in results.values() if r.is_in_scope)
        }
        
    except Exception as e:
        log.error(f"Error in batch capability check: {e}")
        return {"error": str(e)}

