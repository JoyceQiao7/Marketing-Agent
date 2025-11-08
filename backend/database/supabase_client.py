"""
Supabase client for database operations.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from supabase import create_client, Client
from backend.config.settings import settings
from backend.database.models import (
    Question, Comment, AgentResponse, CrawlLog,
    QuestionCreate, QuestionStatus, CrawlStatus
)
from backend.utils.logger import log


class SupabaseClient:
    """Handle all Supabase database operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    # Question Operations
    
    async def create_question(self, question: QuestionCreate) -> Optional[Question]:
        """Create a new question in the database."""
        try:
            data = question.model_dump()
            data['created_at'] = data['created_at'].isoformat()
            data['crawled_at'] = datetime.utcnow().isoformat()
            
            result = self.client.table('questions').insert(data).execute()
            
            if result.data:
                return Question(**result.data[0])
            return None
            
        except Exception as e:
            log.error(f"Error creating question: {e}")
            return None
    
    async def get_question(self, question_id: UUID) -> Optional[Question]:
        """Get a question by ID."""
        try:
            result = self.client.table('questions').select('*').eq('id', str(question_id)).execute()
            
            if result.data:
                return Question(**result.data[0])
            return None
            
        except Exception as e:
            log.error(f"Error getting question: {e}")
            return None
    
    async def get_questions_by_status(self, status: QuestionStatus, limit: int = 100) -> List[Question]:
        """Get questions by status."""
        try:
            result = self.client.table('questions').select('*').eq('status', status.value).limit(limit).execute()
            
            return [Question(**q) for q in result.data]
            
        except Exception as e:
            log.error(f"Error getting questions by status: {e}")
            return []
    
    async def check_question_exists(self, platform: str, post_id: str) -> bool:
        """Check if a question already exists."""
        try:
            result = self.client.table('questions').select('id').eq('platform', platform).eq('post_id', post_id).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            log.error(f"Error checking question existence: {e}")
            return False
    
    async def check_content_hash_exists(self, content_hash: str) -> bool:
        """Check if content hash exists (for deduplication)."""
        try:
            result = self.client.table('questions').select('id').eq('content_hash', content_hash).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            log.error(f"Error checking content hash: {e}")
            return False
    
    async def update_question_status(self, question_id: UUID, status: QuestionStatus) -> bool:
        """Update question status."""
        try:
            result = self.client.table('questions').update({'status': status.value}).eq('id', str(question_id)).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            log.error(f"Error updating question status: {e}")
            return False
    
    async def get_all_questions(self, limit: int = 1000, offset: int = 0) -> List[Question]:
        """Get all questions with pagination."""
        try:
            result = self.client.table('questions').select('*').range(offset, offset + limit - 1).order('crawled_at', desc=True).execute()
            
            return [Question(**q) for q in result.data]
            
        except Exception as e:
            log.error(f"Error getting all questions: {e}")
            return []
    
    # Comment Operations
    
    async def create_comment(self, comment: Comment) -> Optional[Comment]:
        """Create a new comment."""
        try:
            data = comment.model_dump()
            data['created_at'] = data['created_at'].isoformat()
            
            result = self.client.table('comments').insert(data).execute()
            
            if result.data:
                return Comment(**result.data[0])
            return None
            
        except Exception as e:
            log.error(f"Error creating comment: {e}")
            return None
    
    async def get_comments_for_question(self, question_id: UUID) -> List[Comment]:
        """Get all comments for a question."""
        try:
            result = self.client.table('comments').select('*').eq('question_id', str(question_id)).execute()
            
            return [Comment(**c) for c in result.data]
            
        except Exception as e:
            log.error(f"Error getting comments: {e}")
            return []
    
    # Agent Response Operations
    
    async def create_agent_response(self, response: AgentResponse) -> Optional[AgentResponse]:
        """Create a new agent response."""
        try:
            data = response.model_dump()
            data['created_at'] = data['created_at'].isoformat()
            if data.get('posted_at'):
                data['posted_at'] = data['posted_at'].isoformat()
            
            result = self.client.table('agent_responses').insert(data).execute()
            
            if result.data:
                return AgentResponse(**result.data[0])
            return None
            
        except Exception as e:
            log.error(f"Error creating agent response: {e}")
            return None
    
    async def get_agent_response(self, question_id: UUID) -> Optional[AgentResponse]:
        """Get agent response for a question."""
        try:
            result = self.client.table('agent_responses').select('*').eq('question_id', str(question_id)).execute()
            
            if result.data:
                return AgentResponse(**result.data[0])
            return None
            
        except Exception as e:
            log.error(f"Error getting agent response: {e}")
            return None
    
    async def update_response_posted(self, response_id: UUID, posted: bool, posted_at: Optional[datetime] = None) -> bool:
        """Update response posted status."""
        try:
            data = {'posted': posted}
            if posted_at:
                data['posted_at'] = posted_at.isoformat()
            
            result = self.client.table('agent_responses').update(data).eq('id', str(response_id)).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            log.error(f"Error updating response posted status: {e}")
            return False
    
    # Crawl Log Operations
    
    async def create_crawl_log(self, log_entry: CrawlLog) -> Optional[CrawlLog]:
        """Create a crawl log entry."""
        try:
            data = log_entry.model_dump()
            data['started_at'] = data['started_at'].isoformat()
            if data.get('completed_at'):
                data['completed_at'] = data['completed_at'].isoformat()
            
            result = self.client.table('crawl_logs').insert(data).execute()
            
            if result.data:
                return CrawlLog(**result.data[0])
            return None
            
        except Exception as e:
            log.error(f"Error creating crawl log: {e}")
            return None
    
    async def update_crawl_log(self, log_id: UUID, status: CrawlStatus, items_stored: int, completed_at: datetime, error_message: Optional[str] = None) -> bool:
        """Update crawl log with completion details."""
        try:
            data = {
                'status': status.value,
                'items_stored': items_stored,
                'completed_at': completed_at.isoformat()
            }
            if error_message:
                data['error_message'] = error_message
            
            result = self.client.table('crawl_logs').update(data).eq('id', str(log_id)).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            log.error(f"Error updating crawl log: {e}")
            return False
    
    async def get_recent_crawl_logs(self, limit: int = 10) -> List[CrawlLog]:
        """Get recent crawl logs."""
        try:
            result = self.client.table('crawl_logs').select('*').order('started_at', desc=True).limit(limit).execute()
            
            return [CrawlLog(**log) for log in result.data]
            
        except Exception as e:
            log.error(f"Error getting crawl logs: {e}")
            return []
    
    # Analytics Operations
    
    async def get_question_count_by_status(self) -> dict:
        """Get count of questions by status."""
        try:
            result = self.client.table('questions').select('status').execute()
            
            counts = {}
            for row in result.data:
                status = row['status']
                counts[status] = counts.get(status, 0) + 1
            
            return counts
            
        except Exception as e:
            log.error(f"Error getting question counts: {e}")
            return {}
    
    async def get_question_count_by_platform(self) -> dict:
        """Get count of questions by platform."""
        try:
            result = self.client.table('questions').select('platform').execute()
            
            counts = {}
            for row in result.data:
                platform = row['platform']
                counts[platform] = counts.get(platform, 0) + 1
            
            return counts
            
        except Exception as e:
            log.error(f"Error getting platform counts: {e}")
            return {}
    
    async def get_response_stats(self) -> dict:
        """Get response statistics."""
        try:
            result = self.client.table('agent_responses').select('*').execute()
            
            total = len(result.data)
            posted = sum(1 for r in result.data if r.get('posted'))
            avg_confidence = sum(r.get('confidence_score', 0) for r in result.data) / total if total > 0 else 0
            
            return {
                'total': total,
                'posted': posted,
                'success_rate': posted / total if total > 0 else 0,
                'avg_confidence': avg_confidence
            }
            
        except Exception as e:
            log.error(f"Error getting response stats: {e}")
            return {'total': 0, 'posted': 0, 'success_rate': 0, 'avg_confidence': 0}


# Global instance
db_client = SupabaseClient()

