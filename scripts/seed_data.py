"""
Seed test data for development and testing.
"""
import asyncio
from datetime import datetime, timedelta
from backend.database.models import QuestionCreate, PlatformEnum
from backend.database.supabase_client import db_client
from backend.utils.deduplicator import Deduplicator


async def seed_test_questions():
    """Seed database with test questions."""
    
    deduplicator = Deduplicator()
    
    test_questions = [
        QuestionCreate(
            platform=PlatformEnum.REDDIT,
            post_id="test_reddit_1",
            title="How to generate AI videos automatically?",
            content="I'm looking for ways to create videos using AI. Any recommendations for workflows or tools?",
            author="test_user_1",
            url="https://reddit.com/r/test/comments/test_reddit_1",
            tags=["ai", "video", "automation"],
            upvotes=42,
            created_at=datetime.utcnow() - timedelta(hours=2)
        ),
        QuestionCreate(
            platform=PlatformEnum.REDDIT,
            post_id="test_reddit_2",
            title="Best AI video generation tools in 2024?",
            content="What are the current best tools for AI video generation? I need something for marketing content.",
            author="test_user_2",
            url="https://reddit.com/r/test/comments/test_reddit_2",
            tags=["ai", "video", "tools"],
            upvotes=28,
            created_at=datetime.utcnow() - timedelta(hours=5)
        ),
        QuestionCreate(
            platform=PlatformEnum.QUORA,
            post_id="test_quora_1",
            title="Can AI create professional marketing videos?",
            content="I want to know if AI can create high-quality marketing videos without human intervention.",
            author="test_user_3",
            url="https://quora.com/test_quora_1",
            tags=["ai", "marketing", "video"],
            upvotes=15,
            created_at=datetime.utcnow() - timedelta(hours=8)
        ),
        QuestionCreate(
            platform=PlatformEnum.REDDIT,
            post_id="test_reddit_3",
            title="How does machine learning work in video editing?",
            content="Curious about how ML algorithms are used in modern video editing software.",
            author="test_user_4",
            url="https://reddit.com/r/test/comments/test_reddit_3",
            tags=["machine learning", "video editing"],
            upvotes=67,
            created_at=datetime.utcnow() - timedelta(hours=12)
        ),
        QuestionCreate(
            platform=PlatformEnum.REDDIT,
            post_id="test_reddit_4",
            title="Automated video creation workflows?",
            content="Looking for automated workflows to create video content at scale. Any suggestions?",
            author="test_user_5",
            url="https://reddit.com/r/test/comments/test_reddit_4",
            tags=["automation", "video", "workflow"],
            upvotes=33,
            created_at=datetime.utcnow() - timedelta(hours=24)
        ),
    ]
    
    print("Seeding test questions...")
    
    created_count = 0
    
    for question in test_questions:
        try:
            # Check if exists
            exists = await db_client.check_question_exists(
                question.platform.value,
                question.post_id
            )
            
            if not exists:
                result = await db_client.create_question(question)
                if result:
                    created_count += 1
                    print(f"✅ Created: {question.title[:50]}...")
            else:
                print(f"⏭️  Skipped (exists): {question.title[:50]}...")
                
        except Exception as e:
            print(f"❌ Error creating question: {e}")
    
    print(f"\n✅ Seeding complete! Created {created_count} questions.")


async def main():
    """Main function."""
    await seed_test_questions()


if __name__ == "__main__":
    asyncio.run(main())

