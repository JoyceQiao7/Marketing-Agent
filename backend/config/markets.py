"""
Market configuration system for multi-market lead generation.
Each market defines target platforms, keywords, tone, and context.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PlatformConfig:
    """Configuration for a platform within a market."""
    subreddits: List[str] = None
    topics: List[str] = None
    keywords: List[str] = None
    min_upvotes: int = 3
    search_queries: List[str] = None


@dataclass
class MarketConfig:
    """Configuration for a target market segment."""
    name: str
    description: str
    platforms: List[str]
    reddit: Optional[PlatformConfig] = None
    quora: Optional[PlatformConfig] = None
    twitter: Optional[PlatformConfig] = None
    tone: str = "helpful, professional"
    target_pain: str = ""
    mulan_context: str = ""
    workflow_examples: Dict[str, str] = None
    min_confidence_score: float = 0.7
    crawl_interval_hours: int = 6
    max_posts_per_day: int = 20
    
    def __post_init__(self):
        """Initialize default values."""
        if self.workflow_examples is None:
            self.workflow_examples = {}


# Market Definitions
MARKETS = {
    "indie_authors": MarketConfig(
        name="indie_authors",
        description="Independent authors, self-publishers, and writers",
        platforms=["reddit", "quora"],
        reddit=PlatformConfig(
            subreddits=[
                "selfpublish", "writing", "authors", "kindle", "WritingHub",
                "PubTips", "selfpublishing", "bookmarketing"
            ],
            keywords=[
                "book trailer", "author website", "book marketing",
                "book cover video", "author branding", "book promotion",
                "book video", "author video", "promote my book",
                "market my novel", "author platform", "book advertising"
            ],
            min_upvotes=2,
            search_queries=[
                "book trailer", "market my book", "promote novel",
                "author branding", "book marketing video"
            ]
        ),
        quora=PlatformConfig(
            topics=["Self-Publishing", "Book Marketing", "Writing", "Authors"],
            keywords=[
                "publish my book", "market my book", "book trailer",
                "promote book", "author website"
            ]
        ),
        tone="encouraging, creative, supportive",
        target_pain="marketing their books, creating compelling promotional content, building author brand",
        mulan_context="video for book promotion, author branding, book trailers, reader engagement",
        workflow_examples={
            "book_trailer": "https://app.mulan.ai/workflow/book-trailer",
            "author_intro": "https://app.mulan.ai/workflow/author-intro",
            "book_teaser": "https://app.mulan.ai/workflow/book-teaser"
        },
        min_confidence_score=0.65,
        crawl_interval_hours=6,
        max_posts_per_day=15
    ),
    
    "course_creators": MarketConfig(
        name="course_creators",
        description="Online educators, course creators, and e-learning professionals",
        platforms=["reddit", "twitter"],
        reddit=PlatformConfig(
            subreddits=[
                "teachonline", "elearning", "onlineeducation", "Udemy",
                "coursecreators", "instructionaldesign", "OnlineEducation"
            ],
            keywords=[
                "course video", "lecture recording", "student engagement",
                "online course", "teaching video", "educational content",
                "course creation", "screen recording", "video lessons",
                "course marketing", "explainer video", "tutorial video"
            ],
            min_upvotes=3,
            search_queries=[
                "create course videos", "record lectures", "course content",
                "teaching online", "educational videos"
            ]
        ),
        tone="professional, educational, helpful",
        target_pain="creating engaging course content, lecture recordings, student retention",
        mulan_context="educational video, course content, lecture recording, student engagement",
        workflow_examples={
            "lecture_video": "https://app.mulan.ai/workflow/lecture",
            "course_promo": "https://app.mulan.ai/workflow/course-promo",
            "explainer": "https://app.mulan.ai/workflow/explainer"
        },
        min_confidence_score=0.70,
        crawl_interval_hours=8,
        max_posts_per_day=12
    ),
    
    "hr_professionals": MarketConfig(
        name="hr_professionals",
        description="HR, L&D, and corporate training professionals",
        platforms=["reddit", "linkedin"],
        reddit=PlatformConfig(
            subreddits=[
                "humanresources", "AskHR", "recruiting", "LearnAndDevelop",
                "corporatetraining", "TalentDevelopment"
            ],
            keywords=[
                "training video", "employee onboarding", "corporate learning",
                "hr video", "training materials", "employee training",
                "onboarding video", "compliance training", "learning management",
                "employee engagement", "training content"
            ],
            min_upvotes=4,
            search_queries=[
                "training videos", "employee onboarding", "corporate training",
                "hr content", "learning materials"
            ]
        ),
        tone="professional, ROI-focused, efficient",
        target_pain="creating scalable training content, employee onboarding, compliance training",
        mulan_context="corporate training video, employee onboarding, compliance content, L&D materials",
        workflow_examples={
            "onboarding": "https://app.mulan.ai/workflow/onboarding",
            "training": "https://app.mulan.ai/workflow/training",
            "compliance": "https://app.mulan.ai/workflow/compliance"
        },
        min_confidence_score=0.75,
        crawl_interval_hours=12,
        max_posts_per_day=10
    ),
    
    "nonprofits": MarketConfig(
        name="nonprofits",
        description="Nonprofit organizations, fundraisers, and social impact professionals",
        platforms=["reddit", "facebook"],
        reddit=PlatformConfig(
            subreddits=[
                "nonprofit", "fundraising", "charity", "socialgood",
                "NGO", "nonprofitmarketing"
            ],
            keywords=[
                "fundraising video", "donor outreach", "impact storytelling",
                "nonprofit video", "donation campaign", "charity video",
                "impact video", "cause marketing", "volunteer recruitment",
                "grant video", "mission video"
            ],
            min_upvotes=3,
            search_queries=[
                "fundraising video", "nonprofit marketing", "donor engagement",
                "impact storytelling", "charity promotion"
            ]
        ),
        tone="empathetic, mission-focused, inspiring",
        target_pain="fundraising, donor engagement, impact storytelling, volunteer recruitment",
        mulan_context="fundraising video, impact storytelling, donor engagement, cause marketing",
        workflow_examples={
            "fundraising": "https://app.mulan.ai/workflow/fundraising",
            "impact_story": "https://app.mulan.ai/workflow/impact-story",
            "volunteer": "https://app.mulan.ai/workflow/volunteer-recruitment"
        },
        min_confidence_score=0.70,
        crawl_interval_hours=12,
        max_posts_per_day=8
    ),
    
    "b2b_industrial": MarketConfig(
        name="b2b_industrial",
        description="Industrial B2B, manufacturing, and technical product companies",
        platforms=["reddit", "linkedin"],
        reddit=PlatformConfig(
            subreddits=[
                "manufacturing", "industrial", "engineering", "B2B",
                "sales", "ProductManagement", "SaaS"
            ],
            keywords=[
                "product demo", "technical documentation", "sales enablement",
                "product video", "demo video", "explainer video",
                "technical video", "product training", "sales video",
                "customer onboarding", "product walkthrough"
            ],
            min_upvotes=5,
            search_queries=[
                "product demo video", "technical documentation", "sales enablement",
                "product training", "customer onboarding"
            ]
        ),
        tone="technical, efficiency-focused, ROI-driven",
        target_pain="product demonstrations, technical documentation, sales enablement, customer training",
        mulan_context="product demo, technical explainer, sales enablement, customer training video",
        workflow_examples={
            "product_demo": "https://app.mulan.ai/workflow/product-demo",
            "technical_docs": "https://app.mulan.ai/workflow/technical-docs",
            "sales_enablement": "https://app.mulan.ai/workflow/sales-enablement"
        },
        min_confidence_score=0.80,
        crawl_interval_hours=24,
        max_posts_per_day=5
    ),
    
    # General catch-all market for broader video-related queries
    "general_video": MarketConfig(
        name="general_video",
        description="General video creation, editing, and production",
        platforms=["reddit", "quora"],
        reddit=PlatformConfig(
            subreddits=[
                "videoproduction", "videoediting", "VideoEditing", "Filmmakers",
                "videography", "contentcreation"
            ],
            keywords=[
                "ai video", "video creation", "video editing", "video tool",
                "make videos", "video generator", "automated video",
                "text to video", "video ai", "video software"
            ],
            min_upvotes=5,
            search_queries=[
                "ai video", "automated video", "video creation tool",
                "text to video", "video generator"
            ]
        ),
        tone="helpful, enthusiastic, informative",
        target_pain="video creation, editing complexity, time-consuming production",
        mulan_context="AI video generation, automated video creation, video editing",
        workflow_examples={
            "general_video": "https://app.mulan.ai/workflow/video-creation"
        },
        min_confidence_score=0.70,
        crawl_interval_hours=6,
        max_posts_per_day=10
    )
}


def get_market_config(market_name: str) -> Optional[MarketConfig]:
    """
    Get configuration for a specific market.
    
    Args:
        market_name: Name of the market
        
    Returns:
        MarketConfig or None if not found
    """
    return MARKETS.get(market_name)


def get_all_markets() -> List[str]:
    """
    Get list of all configured market names.
    
    Returns:
        List of market names
    """
    return list(MARKETS.keys())


def get_markets_for_platform(platform: str) -> List[str]:
    """
    Get all markets that use a specific platform.
    
    Args:
        platform: Platform name (reddit, quora, etc.)
        
    Returns:
        List of market names
    """
    return [
        name for name, config in MARKETS.items()
        if platform in config.platforms
    ]


def get_keywords_for_market(market_name: str, platform: str) -> List[str]:
    """
    Get keywords for a specific market and platform combination.
    
    Args:
        market_name: Name of the market
        platform: Platform name
        
    Returns:
        List of keywords or empty list
    """
    market = get_market_config(market_name)
    if not market:
        return []
    
    platform_config = getattr(market, platform, None)
    if not platform_config:
        return []
    
    return platform_config.keywords or []


def get_workflow_link_for_context(market_name: str, question_text: str) -> str:
    """
    Select appropriate workflow link based on market and question context.
    
    Args:
        market_name: Name of the market
        question_text: Question text to analyze
        
    Returns:
        Workflow URL
    """
    market = get_market_config(market_name)
    if not market or not market.workflow_examples:
        return "https://app.mulan.ai"
    
    question_lower = question_text.lower()
    
    # Simple keyword matching for workflow selection
    # Could be enhanced with AI/NLP in the future
    for workflow_key, workflow_url in market.workflow_examples.items():
        if workflow_key.replace("_", " ") in question_lower:
            return workflow_url
    
    # Return first workflow as default
    return list(market.workflow_examples.values())[0]

