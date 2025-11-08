"""
Quora-specific crawler implementation using Selenium.
Note: Quora doesn't have an official API, so we use web scraping with Selenium.
"""
from typing import List
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from backend.crawler.base_crawler import BaseCrawler
from backend.database.models import QuestionCreate, Comment, PlatformEnum
from backend.config.settings import settings
from backend.utils.logger import log
from backend.utils.deduplicator import Deduplicator


class QuoraCrawler(BaseCrawler):
    """Crawler for Quora platform using Selenium."""
    
    def __init__(self):
        """Initialize Quora crawler."""
        super().__init__("quora")
        self.deduplicator = Deduplicator()
        self.topics = [t.strip() for t in settings.quora_topics.split(',')]
        self.driver = None
        
        log.info(f"Quora crawler initialized for topics: {self.topics}")
    
    def _init_driver(self):
        """Initialize Selenium WebDriver."""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            log.info("Selenium WebDriver initialized")
    
    def _close_driver(self):
        """Close Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    async def fetch_questions(self, limit: int = 100) -> List[QuestionCreate]:
        """
        Fetch questions from Quora topics.
        
        Note: This is a simplified implementation. Quora's structure changes frequently,
        and you may need to update selectors.
        
        Args:
            limit: Maximum number of questions to fetch
            
        Returns:
            List of QuestionCreate objects
        """
        all_questions = []
        
        try:
            self._init_driver()
            
            for topic in self.topics:
                try:
                    self._wait_for_rate_limit()
                    
                    # Navigate to topic page
                    topic_url = f"https://www.quora.com/topic/{topic.replace(' ', '-')}"
                    log.info(f"Fetching from Quora topic: {topic}")
                    
                    self.driver.get(topic_url)
                    time.sleep(3)  # Wait for page load
                    
                    # Scroll to load more questions
                    for _ in range(3):
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                    
                    # Find question elements (selectors may need updating)
                    # This is a simplified version - Quora's actual structure is more complex
                    questions = self._extract_questions_from_page()
                    
                    all_questions.extend(questions[:limit])
                    log.info(f"Fetched {len(questions)} questions from topic: {topic}")
                    
                except Exception as e:
                    log.error(f"Error fetching from Quora topic {topic}: {e}")
                    continue
            
        finally:
            self._close_driver()
        
        return all_questions
    
    def _extract_questions_from_page(self) -> List[QuestionCreate]:
        """
        Extract questions from current Quora page.
        
        Note: Quora's HTML structure changes frequently. This is a template implementation.
        You'll need to inspect the actual page and update selectors.
        
        Returns:
            List of QuestionCreate objects
        """
        questions = []
        
        try:
            # Wait for questions to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )
            
            # Find question links (selector needs to be updated based on actual Quora structure)
            # This is a placeholder - actual implementation requires inspecting Quora's DOM
            question_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/')]")
            
            for elem in question_elements:
                try:
                    question_text = elem.text.strip()
                    question_url = elem.get_attribute('href')
                    
                    # Filter for actual questions
                    if not question_text or not question_url or '?' not in question_text:
                        continue
                    
                    # Filter for relevant content
                    if not self._is_relevant_question(question_text):
                        continue
                    
                    # Extract question ID from URL
                    post_id = self.deduplicator.extract_platform_id(question_url, "quora") or question_url.split('/')[-1]
                    
                    # Generate content hash
                    content_hash = self.deduplicator.generate_content_hash(question_text)
                    
                    question = QuestionCreate(
                        platform=PlatformEnum.QUORA,
                        post_id=post_id,
                        title=question_text,
                        content=question_text,
                        author="unknown",  # Requires additional scraping
                        url=question_url,
                        tags=[],
                        upvotes=0,  # Requires additional scraping
                        created_at=datetime.utcnow()  # Actual date requires additional scraping
                    )
                    
                    questions.append(question)
                    
                except Exception as e:
                    log.error(f"Error extracting question: {e}")
                    continue
        
        except Exception as e:
            log.error(f"Error extracting questions from page: {e}")
        
        return questions
    
    def _is_relevant_question(self, question_text: str) -> bool:
        """
        Check if question is relevant to AI video generation.
        
        Args:
            question_text: Question text
            
        Returns:
            True if relevant
        """
        relevant_keywords = [
            'ai', 'artificial intelligence', 'video', 'generate', 'create',
            'machine learning', 'deep learning', 'animation', 'editing'
        ]
        
        text_lower = question_text.lower()
        return any(keyword in text_lower for keyword in relevant_keywords)
    
    async def fetch_comments(self, question_url: str) -> List[Comment]:
        """
        Fetch comments/answers for a Quora question.
        
        Args:
            question_url: URL of the Quora question
            
        Returns:
            List of Comment objects
        """
        # Placeholder implementation - requires detailed Quora page scraping
        log.warning("Quora comment fetching not fully implemented")
        return []
    
    async def post_response(self, question_url: str, response_text: str) -> bool:
        """
        Post an answer to a Quora question.
        
        Note: Requires authentication and careful implementation to avoid bot detection.
        
        Args:
            question_url: URL of the Quora question
            response_text: Answer text to post
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._init_driver()
            self._wait_for_rate_limit()
            
            # Navigate to question
            self.driver.get(question_url)
            time.sleep(2)
            
            # This requires authentication and finding the answer box
            # Placeholder implementation
            log.warning("Quora answer posting requires manual implementation with authentication")
            
            return False
            
        except Exception as e:
            log.error(f"Error posting to Quora: {e}")
            return False
        finally:
            self._close_driver()

