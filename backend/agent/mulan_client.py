"""
Client for communicating with Mulan Agent API with multi-market support.
"""
from typing import Dict, Optional
import httpx
from backend.config.settings import settings
from backend.config.markets import get_market_config, get_workflow_link_for_context
from backend.utils.logger import log


class MulanClient:
    """Client to interact with Mulan Agent API with market-aware context."""
    
    def __init__(self):
        """Initialize Mulan Agent client."""
        self.base_url = settings.mulan_agent_url.rstrip('/')
        self.api_key = settings.mulan_agent_api_key
        self.timeout = 30.0
        
        log.info(f"Mulan Agent client initialized: {self.base_url}")
    
    async def analyze_question(
        self, 
        question_text: str, 
        question_title: str = "",
        market: Optional[str] = None
    ) -> Dict:
        """
        Send question to Mulan Agent for analysis with market context.
        
        Args:
            question_text: The question content
            question_title: The question title (optional)
            market: Market segment name for context
            
        Returns:
            Dictionary with analysis results:
            {
                "is_in_scope": bool,
                "confidence_score": float,
                "reasoning": str,
                "suggested_workflow": str (optional)
            }
        """
        try:
            # Get market configuration for context
            market_context = {}
            if market:
                market_config = get_market_config(market)
                if market_config:
                    market_context = {
                        "market": market,
                        "tone": market_config.tone,
                        "target_pain": market_config.target_pain,
                        "mulan_context": market_config.mulan_context
                    }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "question": question_text,
                    "title": question_title,
                    "task": "analyze_capability",
                    "market_context": market_context  # Send market context to AI
                }
                
                log.info(f"Sending question to Mulan Agent (market: {market}): {question_title[:50]}...")
                
                response = await client.post(
                    f"{self.base_url}/api/analyze",
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
                
                log.info(f"Received response from Mulan Agent: in_scope={result.get('is_in_scope')}, confidence={result.get('confidence_score')}")
                
                return result
                
        except httpx.HTTPStatusError as e:
            log.error(f"HTTP error from Mulan Agent: {e.response.status_code} - {e.response.text}")
            return {
                "is_in_scope": False,
                "confidence_score": 0.0,
                "reasoning": f"API error: {e.response.status_code}",
                "error": str(e)
            }
        except Exception as e:
            log.error(f"Error communicating with Mulan Agent: {e}")
            return {
                "is_in_scope": False,
                "confidence_score": 0.0,
                "reasoning": "Communication error",
                "error": str(e)
            }
    
    async def generate_response(
        self, 
        question_text: str, 
        market: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> Dict:
        """
        Generate a response for a question using Mulan Agent with market-specific tone.
        
        Args:
            question_text: The question to answer
            market: Market segment for tone and context
            workflow_id: Optional specific workflow ID to use
            
        Returns:
            Dictionary with response:
            {
                "response_text": str,
                "workflow_link": str,
                "confidence": float
            }
        """
        try:
            # Get market configuration for context
            market_context = {}
            tone = "helpful, professional"
            
            if market:
                market_config = get_market_config(market)
                if market_config:
                    tone = market_config.tone
                    market_context = {
                        "market": market,
                        "tone": tone,
                        "target_pain": market_config.target_pain,
                        "mulan_context": market_config.mulan_context
                    }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "question": question_text,
                    "workflow_id": workflow_id,
                    "task": "generate_response",
                    "market_context": market_context,
                    "tone": tone  # Market-specific tone
                }
                
                log.info(f"Generating response from Mulan Agent (market: {market}, tone: {tone})...")
                
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
                
                log.info("Response generated successfully")
                
                return result
                
        except Exception as e:
            log.error(f"Error generating response: {e}")
            return {
                "response_text": None,
                "workflow_link": None,
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def get_workflow_link(self, workflow_id: str) -> Optional[str]:
        """
        Get the public link for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Workflow URL or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                response = await client.get(
                    f"{self.base_url}/api/workflows/{workflow_id}",
                    headers=headers
                )
                
                response.raise_for_status()
                result = response.json()
                
                return result.get("public_url")
                
        except Exception as e:
            log.error(f"Error getting workflow link: {e}")
            return None
    
    async def health_check(self) -> bool:
        """
        Check if Mulan Agent API is available.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
                
        except Exception as e:
            log.error(f"Mulan Agent health check failed: {e}")
            return False


# Global instance
mulan_client = MulanClient()
