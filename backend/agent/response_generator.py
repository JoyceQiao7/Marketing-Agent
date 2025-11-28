"""
Response generator for creating and posting market-aware responses to questions.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from backend.agent.mulan_client import mulan_client
from backend.database.models import Question, AgentResponse, QuestionStatus
from backend.database.supabase_client import db_client
from backend.crawler.crawler_manager import crawler_manager
from backend.config.settings import settings
from backend.config.markets import get_market_config, get_workflow_link_for_context
from backend.utils.logger import log


class ResponseGenerator:
    """Generate and post market-aware responses to questions."""
    
    def __init__(self):
        """Initialize response generator."""
        self.auto_post_enabled = settings.auto_post_enabled
        log.info(f"Response generator initialized (auto_post: {self.auto_post_enabled})")
    
    async def generate_response(self, question: Question, agent_response: AgentResponse) -> Optional[str]:
        """
        Generate a market-aware response for a question.
        
        Args:
            question: Question to answer
            agent_response: Agent response with analysis
            
        Returns:
            Generated response text or None
        """
        try:
            log.info(f"Generating response for question: {question.id} (market: {question.market})")
            
            # Get market configuration
            market_config = get_market_config(question.market)
            
            # Select appropriate workflow link based on question content
            workflow_link = agent_response.workflow_link
            if not workflow_link and market_config:
                workflow_link = get_workflow_link_for_context(
                    question.market,
                    question.content
                )
            
            # Generate response using Mulan Agent with market context
            response_data = await mulan_client.generate_response(
                question_text=question.content,
                market=question.market
            )
            
            response_text = response_data.get("response_text")
            
            if not response_text:
                log.error("Failed to generate response text")
                return None
            
            # Format response with market-specific template
            formatted_response = self._format_response(
                response_text=response_text,
                workflow_link=workflow_link,
                market=question.market
            )
            
            # Update agent response with generated text
            agent_response.response_text = formatted_response
            
            log.info(f"Response generated successfully for question {question.id}")
            
            return formatted_response
            
        except Exception as e:
            log.error(f"Error generating response: {e}")
            return None
    
    def _format_response(
        self, 
        response_text: str, 
        workflow_link: Optional[str], 
        market: Optional[str]
    ) -> str:
        """
        Format response with workflow link and disclosure.
        
        Args:
            response_text: Generated response text
            workflow_link: Workflow URL
            market: Market segment
            
        Returns:
            Formatted response string
        """
        # Start with the AI-generated response
        formatted = response_text
        
        # Add workflow link if available
        if workflow_link:
            formatted += f"\n\nYou might find this helpful: {workflow_link}"
        
        # Add disclosure (important for transparency and platform compliance)
        formatted += "\n\n*Disclosure: I work with Mulan AI, which offers tools for creating videos easily.*"
        
        return formatted
    
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
            
            # Get appropriate crawler for the platform and market
            crawler = crawler_manager.get_crawler(
                question.platform.value,
                market=question.market
            )
            
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
            
            # Check confidence threshold (market-specific)
            market_config = get_market_config(question.market)
            min_confidence = market_config.min_confidence_score if market_config else settings.min_confidence_score
            
            if agent_response.confidence_score < min_confidence:
                log.info(f"Question {question_id} confidence {agent_response.confidence_score} below threshold {min_confidence}, marking as ignored")
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
    
    async def process_pending_questions(self, limit: int = 10, market: Optional[str] = None) -> int:
        """
        Process pending questions that have agent responses.
        
        Args:
            limit: Maximum number of questions to process
            market: Optional filter by market
            
        Returns:
            Number of questions processed successfully
        """
        try:
            # Get pending questions (optionally filtered by market)
            pending_questions = await db_client.get_questions_by_status(
                QuestionStatus.PENDING,
                limit=limit,
                market=market
            )
            
            log.info(f"Processing {len(pending_questions)} pending questions" + 
                    (f" for market '{market}'" if market else ""))
            
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
