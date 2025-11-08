"""
Rate limiting implementation to respect platform API limits.
"""
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict
import redis
from backend.config.settings import settings
from backend.utils.logger import log


class RateLimiter:
    """Rate limiter using Redis for distributed rate limiting."""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        self.max_requests = settings.max_requests_per_minute
        
    def _get_key(self, identifier: str) -> str:
        """Generate Redis key for rate limiting."""
        minute = datetime.now().strftime("%Y-%m-%d-%H-%M")
        return f"rate_limit:{identifier}:{minute}"
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed based on rate limits.
        
        Args:
            identifier: Unique identifier for rate limiting (e.g., 'reddit', 'quora')
            
        Returns:
            True if request is allowed, False otherwise
        """
        key = self._get_key(identifier)
        
        try:
            current_count = self.redis_client.get(key)
            
            if current_count is None:
                # First request in this minute
                self.redis_client.setex(key, 60, 1)
                return True
            
            if int(current_count) >= self.max_requests:
                log.warning(f"Rate limit exceeded for {identifier}")
                return False
            
            # Increment counter
            self.redis_client.incr(key)
            return True
            
        except Exception as e:
            log.error(f"Rate limiter error: {e}")
            # Allow request if rate limiter fails
            return True
    
    def wait_if_needed(self, identifier: str):
        """Block until rate limit allows request."""
        while not self.is_allowed(identifier):
            log.info(f"Rate limit reached for {identifier}, waiting...")
            time.sleep(1)
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for current minute."""
        key = self._get_key(identifier)
        
        try:
            current_count = self.redis_client.get(key)
            if current_count is None:
                return self.max_requests
            return max(0, self.max_requests - int(current_count))
        except Exception as e:
            log.error(f"Error getting remaining requests: {e}")
            return self.max_requests


class SimpleRateLimiter:
    """In-memory rate limiter for local development."""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.max_requests = settings.max_requests_per_minute
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed based on rate limits."""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > minute_ago
        ]
        
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        self.requests[identifier].append(now)
        return True
    
    def wait_if_needed(self, identifier: str):
        """Block until rate limit allows request."""
        while not self.is_allowed(identifier):
            time.sleep(1)


# Factory function
def get_rate_limiter() -> RateLimiter:
    """Get appropriate rate limiter based on environment."""
    try:
        return RateLimiter()
    except Exception as e:
        log.warning(f"Failed to initialize Redis rate limiter, using simple rate limiter: {e}")
        return SimpleRateLimiter()

