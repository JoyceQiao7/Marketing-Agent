"""
Shared dependencies for FastAPI routes.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.database.supabase_client import db_client, SupabaseClient
from backend.crawler.crawler_manager import crawler_manager, CrawlerManager
from backend.agent.mulan_client import mulan_client, MulanClient
from backend.agent.capability_checker import capability_checker, CapabilityChecker
from backend.agent.response_generator import response_generator, ResponseGenerator
from backend.utils.logger import log


security = HTTPBearer(auto_error=False)


def get_db_client() -> SupabaseClient:
    """Dependency to get database client."""
    return db_client


def get_crawler_manager() -> CrawlerManager:
    """Dependency to get crawler manager."""
    return crawler_manager


def get_mulan_client() -> MulanClient:
    """Dependency to get Mulan client."""
    return mulan_client


def get_capability_checker() -> CapabilityChecker:
    """Dependency to get capability checker."""
    return capability_checker


def get_response_generator() -> ResponseGenerator:
    """Dependency to get response generator."""
    return response_generator


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> bool:
    """
    Verify API key for authenticated endpoints.
    
    Note: This is a placeholder. In production, implement proper authentication.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials"
        )
    
    # TODO: Implement actual API key verification
    # For now, accept any bearer token
    log.debug(f"API key verification (placeholder)")
    
    return True

