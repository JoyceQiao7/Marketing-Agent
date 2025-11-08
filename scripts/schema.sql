-- Supabase Database Schema for Mulan Marketing Agent
-- Run this SQL in Supabase SQL Editor to set up the database

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

-- Add comments for documentation
COMMENT ON TABLE questions IS 'Stores questions crawled from social media platforms';
COMMENT ON TABLE comments IS 'Stores comments on questions';
COMMENT ON TABLE agent_responses IS 'Stores Mulan Agent analysis and responses';
COMMENT ON TABLE crawl_logs IS 'Logs for crawl operations';

-- Enable Row Level Security (RLS) for better security
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE crawl_logs ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your authentication setup)
-- For now, allow all operations with service role key
CREATE POLICY "Enable all operations for service role" ON questions FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON comments FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON agent_responses FOR ALL USING (true);
CREATE POLICY "Enable all operations for service role" ON crawl_logs FOR ALL USING (true);

