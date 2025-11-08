"""
Reddit-specific crawler implementation using PRAW.
"""
from typing import List
from datetime import datetime
import praw
from praw.models import Submission
from backend.crawler.base_crawler import BaseCrawler
from backend.database.models import QuestionCreate, Comment, PlatformEnum
from backend.config.settings import settings
from backend.utils.logger import log
from backend.utils.deduplicator import Deduplicator


class RedditCrawler(BaseCrawler):
    """Crawler for Reddit platform."""
    
    def __init__(self):
        """Initialize Reddit crawler with PRAW."""
        super().__init__("reddit")
        
        # Initialize Reddit client
        self.reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
            username=settings.reddit_username,
            password=settings.reddit_password
        )
        
        # Parse subreddits from settings
        self.subreddits = [s.strip() for s in settings.reddit_subreddits.split(',')]
        self.deduplicator = Deduplicator()
        
        log.info(f"Reddit crawler initialized for subreddits: {self.subreddits}")
    
    async def fetch_questions(self, limit: int = 100) -> List[QuestionCreate]:
        """
        Fetch questions from configured subreddits.
        
        Args:
            limit: Maximum number of questions to fetch per subreddit
            
        Returns:
            List of QuestionCreate objects
        """
        all_questions = []
        
        for subreddit_name in self.subreddits:
            try:
                self._wait_for_rate_limit()
                
                subreddit = self.reddit.subreddit(subreddit_name)
                log.info(f"Fetching from r/{subreddit_name}")
                
                # Fetch new posts
                for submission in subreddit.new(limit=limit):
                    try:
                        # Filter for question-like posts
                        if self._is_question(submission):
                            question = self._submission_to_question(submission)
                            all_questions.append(question)
                    
                    except Exception as e:
                        log.error(f"Error processing submission {submission.id}: {e}")
                        continue
                
                log.info(f"Fetched {len(all_questions)} questions from r/{subreddit_name}")
                
            except Exception as e:
                log.error(f"Error fetching from r/{subreddit_name}: {e}")
                continue
        
        return all_questions
    
    async def fetch_comments(self, question_url: str) -> List[Comment]:
        """
        Fetch comments for a Reddit post.
        
        Args:
            question_url: URL of the Reddit post
            
        Returns:
            List of Comment objects
        """
        try:
            self._wait_for_rate_limit()
            
            submission = self.reddit.submission(url=question_url)
            submission.comments.replace_more(limit=0)  # Flatten comment tree
            
            comments = []
            for comment in submission.comments.list():
                try:
                    comments.append(Comment(
                        question_id=None,  # Will be set when storing
                        comment_id=comment.id,
                        content=comment.body,
                        author=str(comment.author),
                        upvotes=comment.score,
                        created_at=datetime.fromtimestamp(comment.created_utc)
                    ))
                except Exception as e:
                    log.error(f"Error processing comment: {e}")
                    continue
            
            return comments
            
        except Exception as e:
            log.error(f"Error fetching comments from {question_url}: {e}")
            return []
    
    async def post_response(self, question_url: str, response_text: str) -> bool:
        """
        Post a comment response to a Reddit post.
        
        Args:
            question_url: URL of the Reddit post
            response_text: Response text to post
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._wait_for_rate_limit()
            
            submission = self.reddit.submission(url=question_url)
            comment = submission.reply(response_text)
            
            log.info(f"Posted response to {question_url}: comment ID {comment.id}")
            return True
            
        except Exception as e:
            log.error(f"Error posting response to {question_url}: {e}")
            return False
    
    def _is_question(self, submission: Submission) -> bool:
        """
        Determine if a submission is a question.
        
        Args:
            submission: PRAW Submission object
            
        Returns:
            True if submission appears to be a question
        """
        # Check for question markers
        title_lower = submission.title.lower()
        
        question_markers = ['?', 'how', 'what', 'why', 'when', 'where', 'who', 'can', 'should', 'is it']
        
        # Must have question marker in title
        has_marker = any(marker in title_lower for marker in question_markers)
        
        # Filter for AI/video-related content
        relevant_keywords = [
            'ai', 'artificial intelligence', 'video', 'generate', 'create',
            'machine learning', 'deep learning', 'neural', 'animation',
            'editing', 'production', 'workflow'
        ]
        
        content = (submission.title + ' ' + submission.selftext).lower()
        is_relevant = any(keyword in content for keyword in relevant_keywords)
        
        return has_marker and is_relevant
    
    def _submission_to_question(self, submission: Submission) -> QuestionCreate:
        """
        Convert Reddit submission to QuestionCreate model.
        
        Args:
            submission: PRAW Submission object
            
        Returns:
            QuestionCreate object
        """
        # Extract tags from submission
        tags = []
        if hasattr(submission, 'link_flair_text') and submission.link_flair_text:
            tags.append(submission.link_flair_text)
        
        # Get content
        content = submission.selftext if submission.selftext else submission.title
        
        # Generate content hash for deduplication
        content_hash = self.deduplicator.generate_content_hash(content)
        
        return QuestionCreate(
            platform=PlatformEnum.REDDIT,
            post_id=submission.id,
            title=submission.title,
            content=content,
            author=str(submission.author),
            url=f"https://reddit.com{submission.permalink}",
            tags=tags,
            upvotes=submission.score,
            created_at=datetime.fromtimestamp(submission.created_utc)
        )

