"""
Reddit-specific crawler implementation using PRAW with multi-market support.
"""
from typing import List, Optional
from datetime import datetime, timedelta
import praw
from praw.models import Submission
from backend.crawler.base_crawler import BaseCrawler
from backend.database.models import QuestionCreate, Comment, PlatformEnum
from backend.config.settings import settings
from backend.config.markets import get_market_config, MarketConfig
from backend.utils.logger import log
from backend.utils.deduplicator import Deduplicator


class RedditCrawler(BaseCrawler):
    """Crawler for Reddit platform with market-specific configuration."""
    
    def __init__(self, market_name: Optional[str] = None):
        """
        Initialize Reddit crawler with PRAW.
        
        Args:
            market_name: Optional market segment to configure crawler for
        """
        super().__init__("reddit")
        
        # Initialize Reddit client
        self.reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
            username=settings.reddit_username,
            password=settings.reddit_password
        )
        
        self.market_name = market_name
        self.market_config = None
        
        # Load market configuration if specified
        if market_name:
            self.market_config = get_market_config(market_name)
            if self.market_config and self.market_config.reddit:
                self.subreddits = self.market_config.reddit.subreddits or []
                self.keywords = self.market_config.reddit.keywords or []
                self.min_upvotes = self.market_config.reddit.min_upvotes
                self.search_queries = self.market_config.reddit.search_queries or []
                log.info(f"Reddit crawler initialized for market '{market_name}' with {len(self.subreddits)} subreddits")
            else:
                log.warning(f"No Reddit config found for market '{market_name}', using defaults")
                self._use_defaults()
        else:
            self._use_defaults()
        
        self.deduplicator = Deduplicator()
    
    def _use_defaults(self):
        """Use default configuration from settings."""
        self.subreddits = [s.strip() for s in settings.reddit_subreddits.split(',')]
        self.keywords = ['ai', 'video', 'create', 'generate']
        self.min_upvotes = 1
        self.search_queries = []
        log.info(f"Reddit crawler initialized with default subreddits: {self.subreddits}")
    
    async def fetch_questions(self, limit: int = 100) -> List[QuestionCreate]:
        """
        Fetch questions from configured subreddits using market-specific keywords.
        
        Args:
            limit: Maximum number of questions to fetch per subreddit
            
        Returns:
            List of QuestionCreate objects
        """
        all_questions = []
        posts_per_subreddit = limit // max(len(self.subreddits), 1)
        
        for subreddit_name in self.subreddits:
            try:
                self._wait_for_rate_limit()
                
                subreddit = self.reddit.subreddit(subreddit_name)
                log.info(f"Fetching from r/{subreddit_name} for market '{self.market_name}'")
                
                # Strategy 1: Get new posts and filter
                new_posts = list(subreddit.new(limit=posts_per_subreddit * 2))
                
                # Strategy 2: Search with keywords if available
                if self.search_queries:
                    for query in self.search_queries:
                        try:
                            self._wait_for_rate_limit()
                            search_results = list(subreddit.search(
                                query, 
                                time_filter='week',
                                limit=min(20, posts_per_subreddit)
                            ))
                            new_posts.extend(search_results)
                        except Exception as e:
                            log.error(f"Error searching '{query}' in r/{subreddit_name}: {e}")
                
                # Deduplicate by post ID
                seen_ids = set()
                unique_posts = []
                for post in new_posts:
                    if post.id not in seen_ids:
                        seen_ids.add(post.id)
                        unique_posts.append(post)
                
                # Filter and convert posts
                for submission in unique_posts[:posts_per_subreddit]:
                    try:
                        # Filter for relevant posts
                        if self._is_relevant(submission):
                            question = self._submission_to_question(submission)
                            all_questions.append(question)
                    
                    except Exception as e:
                        log.error(f"Error processing submission {submission.id}: {e}")
                        continue
                
                log.info(f"Fetched {len([q for q in all_questions if q.url.startswith('https://reddit.com')])} questions from r/{subreddit_name}")
                
            except Exception as e:
                log.error(f"Error fetching from r/{subreddit_name}: {e}")
                continue
        
        log.info(f"Total questions fetched for market '{self.market_name}': {len(all_questions)}")
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
                        author=str(comment.author) if comment.author else '[deleted]',
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
    
    def _is_relevant(self, submission: Submission) -> bool:
        """
        Determine if a submission is relevant based on market keywords.
        
        Args:
            submission: PRAW Submission object
            
        Returns:
            True if submission is relevant to the market
        """
        # Check age - only recent posts (last 7 days)
        post_age_days = (datetime.utcnow() - datetime.fromtimestamp(submission.created_utc)).days
        if post_age_days > 7:
            return False
        
        # Check minimum upvotes
        if submission.score < self.min_upvotes:
            return False
        
        # Check for question markers (optional but preferred)
        title_lower = submission.title.lower()
        content = (submission.title + ' ' + submission.selftext).lower()
        
        # Must contain at least one market keyword
        if self.keywords:
            has_keyword = any(keyword.lower() in content for keyword in self.keywords)
            if not has_keyword:
                return False
        
        # Bonus: contains question marker
        question_markers = ['?', 'how ', 'what ', 'why ', 'when ', 'where ', 'who ', 
                           'can i', 'can you', 'should i', 'is it', 'are there',
                           'looking for', 'need help', 'recommendations', 'suggestions']
        has_question = any(marker in content for marker in question_markers)
        
        # Posts with questions get priority but not required
        # This allows for statements of pain/need that aren't explicitly questions
        return True
    
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
        
        # Add subreddit as tag
        tags.append(f"r/{submission.subreddit.display_name}")
        
        # Get content
        content = submission.selftext if submission.selftext else submission.title
        
        # Generate content hash for deduplication
        content_hash = self.deduplicator.generate_content_hash(content)
        
        return QuestionCreate(
            platform=PlatformEnum.REDDIT,
            post_id=submission.id,
            title=submission.title,
            content=content,
            author=str(submission.author) if submission.author else '[deleted]',
            url=f"https://reddit.com{submission.permalink}",
            market=self.market_name or "general_video",  # Default market if not specified
            tags=tags,
            upvotes=submission.score,
            created_at=datetime.fromtimestamp(submission.created_utc)
        )
