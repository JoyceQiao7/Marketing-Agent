"""
Capability checker to determine if questions are answerable by Mulan Agent.
"""
from typing import Dict
from uuid import UUID
from backend.agent.mulan_client import mulan_client
from backend.database.models import Question, AgentResponse
from backend.database.supabase_client import db_client
from backend.config.settings import settings
from backend.utils.logger import log


class CapabilityChecker:
    """Check if questions can be answered by Mulan Agent."""
    
    def __init__(self):
        """Initialize capability checker."""
        self.min_confidence = settings.min_confidence_score
        log.info(f"Capability checker initialized with min confidence: {self.min_confidence}")
    
    async def check_question(self, question: Question) -> AgentResponse:
        """
        Check if a question can be answered by Mulan Agent.
        
        Args:
            question: Question to check
            
        Returns:
            AgentResponse with analysis results
        """
        log.info(f"Checking capability for question: {question.id}")
        
        try:
            # Send question to Mulan Agent
            analysis = await mulan_client.analyze_question(
                question_text=question.content,
                question_title=question.title
            )
            
            is_in_scope = analysis.get("is_in_scope", False)
            confidence_score = analysis.get("confidence_score", 0.0)
            
            # Check if confidence meets minimum threshold
            meets_threshold = confidence_score >= self.min_confidence
            
            log.info(
                f"Question {question.id} analysis: "
                f"in_scope={is_in_scope}, confidence={confidence_score:.2f}, "
                f"meets_threshold={meets_threshold}"
            )
            
            # Create agent response record
            agent_response = AgentResponse(
                question_id=question.id,
                is_in_scope=is_in_scope and meets_threshold,
                confidence_score=confidence_score,
                workflow_link=analysis.get("suggested_workflow"),
                response_text=None,  # Will be generated later if in scope
                posted=False
            )
            
            # Store in database
            stored_response = await db_client.create_agent_response(agent_response)
            
            if stored_response:
                log.info(f"Agent response stored for question {question.id}")
                return stored_response
            else:
                log.error(f"Failed to store agent response for question {question.id}")
                return agent_response
            
        except Exception as e:
            log.error(f"Error checking capability for question {question.id}: {e}")
            
            # Create error response
            error_response = AgentResponse(
                question_id=question.id,
                is_in_scope=False,
                confidence_score=0.0,
                error_message=str(e),
                posted=False
            )
            
            await db_client.create_agent_response(error_response)
            
            return error_response
    
    async def batch_check_questions(self, question_ids: list[UUID]) -> Dict[UUID, AgentResponse]:
        """
        Check multiple questions in batch.
        
        Args:
            question_ids: List of question IDs to check
            
        Returns:
            Dictionary mapping question IDs to AgentResponse objects
        """
        results = {}
        
        for question_id in question_ids:
            question = await db_client.get_question(question_id)
            
            if question:
                response = await self.check_question(question)
                results[question_id] = response
            else:
                log.warning(f"Question {question_id} not found")
        
        return results
    
    def is_answerable(self, agent_response: AgentResponse) -> bool:
        """
        Determine if question is answerable based on agent response.
        
        Args:
            agent_response: Agent response to evaluate
            
        Returns:
            True if question is answerable
        """
        return (
            agent_response.is_in_scope and
            agent_response.confidence_score >= self.min_confidence
        )


# Global instance
capability_checker = CapabilityChecker()

