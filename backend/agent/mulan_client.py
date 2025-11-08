"""
Client for communicating with Mulan Agent API.
"""
from typing import Dict, Optional
import httpx
from backend.config.settings import settings
from backend.utils.logger import log


class MulanClient:
    """Client to interact with Mulan Agent API."""
    
    def __init__(self):
        """Initialize Mulan Agent client."""
        self.base_url = settings.mulan_agent_url.rstrip('/')
        self.api_key = settings.mulan_agent_api_key
        self.timeout = 30.0
        
        log.info(f"Mulan Agent client initialized: {self.base_url}")
    
    async def analyze_question(self, question_text: str, question_title: str = "") -> Dict:
        """
        Send question to Mulan Agent for analysis.
        
        Args:
            question_text: The question content
            question_title: The question title (optional)
            
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
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "question": question_text,
                    "title": question_title,
                    "task": "analyze_capability"
                }
                
                log.info(f"Sending question to Mulan Agent: {question_title[:50]}...")
                
                response = await client.post(
                    f"{self.base_url}/api/analyze",
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
                
                log.info(f"Received response from Mulan Agent: in_scope={result.get('is_in_scope')}")
                
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
    
    async def generate_response(self, question_text: str, workflow_id: Optional[str] = None) -> Dict:
        """
        Generate a response for a question using Mulan Agent.
        
        Args:
            question_text: The question to answer
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
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "question": question_text,
                    "workflow_id": workflow_id,
                    "task": "generate_response"
                }
                
                log.info("Generating response from Mulan Agent...")
                
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

