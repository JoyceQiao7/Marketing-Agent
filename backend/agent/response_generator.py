"""
Response generator for creating and posting responses to questions.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from backend.agent.mulan_client import mulan_client
from backend.database.models import Question, AgentResponse, QuestionStatus
from backend.database.supabase_client import db_client
from backend.crawler.crawler_manager import crawler_manager
from backend.config.settings import settings
from backend.utils.logger import log


class ResponseGenerator:
    """Generate and post responses to questions."""
    
    def __init__(self):
        """Initialize response generator."""
        self.auto_post_enabled = settings.auto_post_enabled
        log.info(f"Response generator initialized (auto_post: {self.auto_post_enabled})")
    
    async def generate_response(self, question: Question, agent_response: AgentResponse) -> Optional[str]:
        """
        Generate a response for a question.
        
        Args:
            question: Question to answer
            agent_response: Agent response with analysis
            
        Returns:
            Generated response text or None
        """
        try:
            log.info(f"Generating response for question: {question.id}")
            
            # Get workflow link
            workflow_link = agent_response.workflow_link
            
            # Generate response using Mulan Agent
            response_data = await mulan_client.generate_response(
                question_text=question.content
            )
            
            response_text = response_data.get("response_text")
            
            if not response_text:
                log.error("Failed to generate response text")
                return None
            
            # Add workflow link to response
            if workflow_link:
                response_text += f"\n\nCheck out this workflow: {workflow_link}"
            
            # Update agent response with generated text
            agent_response.response_text = response_text
            
            log.info(f"Response generated successfully for question {question.id}")
            
            return response_text
            
        except Exception as e:
            log.error(f"Error generating response: {e}")
            return None
    
    async def post_response(self, question: Question, response_text: str) -> bool:
        """
        Post a response to a platform.
        
        Args:
            question: Question to respond to
            response_text: Response text to post
            
        Returns:
            True if posted successfully, False otherwise
        """
        try:
            log.info(f"Posting response to {question.platform} question: {question.id}")
            
            # Get appropriate crawler
            crawler = crawler_manager.get_crawler(question.platform.value)
            
            if not crawler:
                log.error(f"No crawler found for platform: {question.platform}")
                return False
            
            # Post response
            success = await crawler.post_response(question.url, response_text)
            
            if success:
                log.info(f"Response posted successfully to question {question.id}")
                
                # Update question status
                await db_client.update_question_status(question.id, QuestionStatus.ANSWERED)
            else:
                log.error(f"Failed to post response to question {question.id}")
            
            return success
            
        except Exception as e:
            log.error(f"Error posting response: {e}")
            return False
    
    async def process_question(self, question_id: UUID) -> bool:
        """
        Complete workflow: generate and optionally post response.
        
        Args:
            question_id: Question ID to process
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            # Get question and agent response
            question = await db_client.get_question(question_id)
            if not question:
                log.error(f"Question {question_id} not found")
                return False
            
            agent_response = await db_client.get_agent_response(question_id)
            if not agent_response:
                log.error(f"Agent response not found for question {question_id}")
                return False
            
            # Check if question is answerable
            if not agent_response.is_in_scope:
                log.info(f"Question {question_id} is not in scope, marking as ignored")
                await db_client.update_question_status(question_id, QuestionStatus.IGNORED)
                return False
            
            # Update status to processing
            await db_client.update_question_status(question_id, QuestionStatus.PROCESSING)
            
            # Generate response
            response_text = await self.generate_response(question, agent_response)
            
            if not response_text:
                log.error(f"Failed to generate response for question {question_id}")
                await db_client.update_question_status(question_id, QuestionStatus.ERROR)
                return False
            
            # Update agent response in database
            agent_response.response_text = response_text
            
            # Post response if auto-post is enabled
            posted = False
            if self.auto_post_enabled:
                posted = await self.post_response(question, response_text)
                
                # Update agent response
                await db_client.update_response_posted(
                    agent_response.id,
                    posted=posted,
                    posted_at=datetime.utcnow() if posted else None
                )
            else:
                log.info(f"Auto-post disabled, response generated but not posted for question {question_id}")
                # Still mark as answered since response is ready
                await db_client.update_question_status(question_id, QuestionStatus.ANSWERED)
            
            return True
            
        except Exception as e:
            log.error(f"Error processing question {question_id}: {e}")
            await db_client.update_question_status(question_id, QuestionStatus.ERROR)
            return False
    
    async def process_pending_questions(self, limit: int = 10) -> int:
        """
        Process pending questions that have agent responses.
        
        Args:
            limit: Maximum number of questions to process
            
        Returns:
            Number of questions processed successfully
        """
        try:
            # Get pending questions
            pending_questions = await db_client.get_questions_by_status(
                QuestionStatus.PENDING,
                limit=limit
            )
            
            log.info(f"Processing {len(pending_questions)} pending questions")
            
            processed_count = 0
            
            for question in pending_questions:
                # Check if agent response exists
                agent_response = await db_client.get_agent_response(question.id)
                
                if agent_response and agent_response.is_in_scope:
                    success = await self.process_question(question.id)
                    if success:
                        processed_count += 1
            
            log.info(f"Processed {processed_count} questions successfully")
            
            return processed_count
            
        except Exception as e:
            log.error(f"Error processing pending questions: {e}")
            return 0


# Global instance
response_generator = ResponseGenerator()

