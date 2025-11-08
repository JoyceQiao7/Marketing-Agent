"""
Pydantic models for database entities.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field


class PlatformEnum(str, Enum):
    """Supported platforms."""
    REDDIT = "reddit"
    QUORA = "quora"
    TWITTER = "twitter"
    OTHER = "other"


class QuestionStatus(str, Enum):
    """Question processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    ANSWERED = "answered"
    IGNORED = "ignored"
    ERROR = "error"


class CrawlStatus(str, Enum):
    """Crawl job status."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


# Database Models

class Question(BaseModel):
    """Question entity from social media platforms."""
    id: UUID = Field(default_factory=uuid4)
    platform: PlatformEnum
    post_id: str
    title: str
    content: str
    author: str
    url: str
    tags: List[str] = Field(default_factory=list)
    upvotes: int = 0
    status: QuestionStatus = QuestionStatus.PENDING
    content_hash: Optional[str] = None
    created_at: datetime
    crawled_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform": "reddit",
                "post_id": "abc123",
                "title": "How to generate AI videos?",
                "content": "I want to create videos using AI...",
                "author": "user123",
                "url": "https://reddit.com/r/ai/comments/abc123",
                "tags": ["ai", "video"],
                "upvotes": 42,
                "status": "pending"
            }
        }


class Comment(BaseModel):
    """Comment on a question."""
    id: UUID = Field(default_factory=uuid4)
    question_id: UUID
    comment_id: str
    content: str
    author: str
    upvotes: int = 0
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "123e4567-e89b-12d3-a456-426614174000",
                "comment_id": "xyz789",
                "content": "You should try...",
                "author": "helpful_user",
                "upvotes": 5
            }
        }


class AgentResponse(BaseModel):
    """Response from Mulan Agent."""
    id: UUID = Field(default_factory=uuid4)
    question_id: UUID
    is_in_scope: bool
    confidence_score: float
    workflow_link: Optional[str] = None
    response_text: Optional[str] = None
    posted: bool = False
    posted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "123e4567-e89b-12d3-a456-426614174000",
                "is_in_scope": True,
                "confidence_score": 0.85,
                "workflow_link": "https://mulan.ai/workflow/123",
                "response_text": "You can use our AI workflow...",
                "posted": True
            }
        }


class CrawlLog(BaseModel):
    """Log entry for crawl jobs."""
    id: UUID = Field(default_factory=uuid4)
    platform: str
    status: CrawlStatus
    items_found: int = 0
    items_stored: int = 0
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform": "reddit",
                "status": "success",
                "items_found": 50,
                "items_stored": 45,
                "started_at": "2024-01-01T00:00:00Z",
                "completed_at": "2024-01-01T00:05:00Z"
            }
        }


# Request/Response Models for API

class QuestionCreate(BaseModel):
    """Schema for creating a question."""
    platform: PlatformEnum
    post_id: str
    title: str
    content: str
    author: str
    url: str
    tags: List[str] = Field(default_factory=list)
    upvotes: int = 0
    created_at: datetime


class QuestionUpdate(BaseModel):
    """Schema for updating a question."""
    status: Optional[QuestionStatus] = None
    upvotes: Optional[int] = None


class AgentResponseCreate(BaseModel):
    """Schema for creating an agent response."""
    question_id: UUID
    is_in_scope: bool
    confidence_score: float
    workflow_link: Optional[str] = None
    response_text: Optional[str] = None


class CrawlTriggerRequest(BaseModel):
    """Request to trigger a manual crawl."""
    platform: PlatformEnum
    limit: Optional[int] = 100


class AnalyticsResponse(BaseModel):
    """Analytics summary response."""
    total_questions: int
    questions_by_status: dict
    questions_by_platform: dict
    total_responses: int
    response_success_rate: float
    avg_confidence_score: float

