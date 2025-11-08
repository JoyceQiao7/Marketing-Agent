"""
Database setup script to initialize Supabase tables.

Run this script after setting up your Supabase project to create the necessary tables.
"""
import asyncio
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# SQL to create tables
CREATE_TABLES_SQL = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create questions table
CREATE TABLE IF NOT EXISTS questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(50) NOT NULL,
    post_id VARCHAR(255) NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    upvotes INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    content_hash VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    crawled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(platform, post_id)
);

-- Create comments table
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    comment_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(255) NOT NULL,
    upvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE(question_id, comment_id)
);

-- Create agent_responses table
CREATE TABLE IF NOT EXISTS agent_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    is_in_scope BOOLEAN NOT NULL,
    confidence_score FLOAT NOT NULL,
    workflow_link TEXT,
    response_text TEXT,
    posted BOOLEAN DEFAULT FALSE,
    posted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    error_message TEXT,
    UNIQUE(question_id)
);

-- Create crawl_logs table
CREATE TABLE IF NOT EXISTS crawl_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    items_found INTEGER DEFAULT 0,
    items_stored INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_questions_platform ON questions(platform);
CREATE INDEX IF NOT EXISTS idx_questions_status ON questions(status);
CREATE INDEX IF NOT EXISTS idx_questions_crawled_at ON questions(crawled_at DESC);
CREATE INDEX IF NOT EXISTS idx_questions_content_hash ON questions(content_hash);
CREATE INDEX IF NOT EXISTS idx_comments_question_id ON comments(question_id);
CREATE INDEX IF NOT EXISTS idx_agent_responses_question_id ON agent_responses(question_id);
CREATE INDEX IF NOT EXISTS idx_agent_responses_is_in_scope ON agent_responses(is_in_scope);
CREATE INDEX IF NOT EXISTS idx_crawl_logs_platform ON crawl_logs(platform);
CREATE INDEX IF NOT EXISTS idx_crawl_logs_started_at ON crawl_logs(started_at DESC);
"""


def setup_database():
    """Set up database tables and indexes."""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return
    
    try:
        print("Connecting to Supabase...")
        client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("Creating tables and indexes...")
        
        # Note: Supabase PostgreSQL client may not support raw SQL execution directly
        # You may need to run this SQL manually in Supabase SQL Editor or use psycopg2
        
        print("\n" + "="*60)
        print("IMPORTANT: Please run the following SQL in your Supabase SQL Editor:")
        print("="*60)
        print(CREATE_TABLES_SQL)
        print("="*60)
        print("\nAlternatively, you can:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the SQL above")
        print("4. Click 'Run' to execute")
        print("\nOr use the provided SQL file: scripts/schema.sql")
        
        # Test connection
        result = client.table('questions').select("count").execute()
        print("\n✅ Database connection successful!")
        
    except Exception as e:
        print(f"\n❌ Error setting up database: {e}")
        print("\nPlease manually run the SQL commands in Supabase SQL Editor.")


if __name__ == "__main__":
    setup_database()

