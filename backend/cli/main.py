"""
Command-line interface for Mulan Marketing Agent.
Provides tools for managing leads, responses, and crawls.
"""
import click
import asyncio
from tabulate import tabulate
from datetime import datetime, timedelta
from typing import Optional
from backend.database.supabase_client import db_client
from backend.config.markets import get_all_markets, get_market_config
from backend.crawler.crawler_manager import crawler_manager
from backend.agent.response_generator import response_generator
from backend.utils.logger import log


@click.group()
def cli():
    """Mulan Marketing Agent CLI - Multi-market lead generation tool."""
    pass


@cli.command()
@click.option('--market', required=True, help='Market segment (indie_authors, course_creators, etc.)')
@click.option('--status', default='pending', help='Question status filter')
@click.option('--limit', default=10, help='Number of results')
@click.option('--min-score', type=float, default=None, help='Minimum confidence score')
def leads(market, status, limit, min_score):
    """
    List top leads for a specific market.
    
    Example:
        python -m backend.cli.main leads --market indie_authors --limit 10
    """
    try:
        questions = asyncio.run(db_client.get_questions(
            market=market,
            status=status,
            min_score=min_score,
            limit=limit
        ))
        
        if not questions:
            click.echo(f"No {status} leads found for market '{market}'")
            return
        
        table_data = []
        for q in questions:
            # Get agent response for score
            response = asyncio.run(db_client.get_agent_response(q.id))
            score = response.confidence_score if response else 0.0
            
            table_data.append([
                str(q.id)[:8] + '...',
                q.title[:40] + ('...' if len(q.title) > 40 else ''),
                q.platform.value,
                f"{score:.2f}",
                q.upvotes,
                q.created_at.strftime('%Y-%m-%d')
            ])
        
        click.echo(f"\n{'='*80}")
        click.echo(f"Top Leads for Market: {market.upper()}")
        click.echo(f"{'='*80}\n")
        
        click.echo(tabulate(
            table_data,
            headers=['ID', 'Title', 'Platform', 'Score', 'Upvotes', 'Date'],
            tablefmt='grid'
        ))
        
        click.echo(f"\nTotal: {len(questions)} leads\n")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command()
@click.argument('question_id')
def show(question_id):
    """
    Show detailed information for a specific question and its generated response.
    
    Example:
        python -m backend.cli.main show abc123...
    """
    try:
        # Get question
        question = asyncio.run(db_client.get_question(question_id))
        if not question:
            click.echo(f"Question {question_id} not found", err=True)
            return
        
        # Get response
        response = asyncio.run(db_client.get_agent_response(question_id))
        
        click.echo(f"\n{'='*80}")
        click.echo(f"QUESTION DETAILS")
        click.echo(f"{'='*80}")
        click.echo(f"ID:         {question.id}")
        click.echo(f"Market:     {question.market}")
        click.echo(f"Platform:   {question.platform.value}")
        click.echo(f"Status:     {question.status.value}")
        click.echo(f"Author:     {question.author}")
        click.echo(f"Upvotes:    {question.upvotes}")
        click.echo(f"URL:        {question.url}")
        click.echo(f"Created:    {question.created_at}")
        click.echo(f"\nTitle:\n{question.title}")
        click.echo(f"\nContent:\n{question.content[:500]}...")
        
        if response:
            click.echo(f"\n{'='*80}")
            click.echo(f"GENERATED RESPONSE (Score: {response.confidence_score:.2f})")
            click.echo(f"{'='*80}")
            click.echo(f"In Scope:   {'Yes' if response.is_in_scope else 'No'}")
            click.echo(f"Posted:     {'Yes' if response.posted else 'No'}")
            if response.posted_at:
                click.echo(f"Posted At:  {response.posted_at}")
            if response.workflow_link:
                click.echo(f"Workflow:   {response.workflow_link}")
            
            if response.response_text:
                click.echo(f"\nResponse Text:\n{response.response_text}")
        else:
            click.echo(f"\n(No response generated yet)")
        
        click.echo(f"\n{'='*80}\n")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command()
@click.argument('question_id')
@click.option('--approve', is_flag=True, help='Confirm posting')
def post(question_id, approve):
    """
    Post a response to a question after approval.
    
    Example:
        python -m backend.cli.main post abc123... --approve
    """
    if not approve:
        click.echo("Use --approve flag to confirm posting")
        return
    
    try:
        # Get question and response
        question = asyncio.run(db_client.get_question(question_id))
        if not question:
            click.echo(f"Question {question_id} not found", err=True)
            return
        
        response = asyncio.run(db_client.get_agent_response(question_id))
        if not response or not response.response_text:
            click.echo(f"No response generated for this question", err=True)
            return
        
        if response.posted:
            click.echo(f"Response already posted at {response.posted_at}", err=True)
            return
        
        # Show what will be posted
        click.echo(f"\n{'='*80}")
        click.echo(f"POSTING TO: {question.platform.value.upper()} ({question.market})")
        click.echo(f"{'='*80}")
        click.echo(f"Question: {question.title}")
        click.echo(f"URL: {question.url}")
        click.echo(f"\nResponse:\n{response.response_text}")
        click.echo(f"{'='*80}\n")
        
        if click.confirm('Proceed with posting?'):
            success = asyncio.run(response_generator.post_response(question, response.response_text))
            
            if success:
                # Update response as posted
                asyncio.run(db_client.update_response_posted(
                    response.id,
                    posted=True,
                    posted_at=datetime.utcnow()
                ))
                click.echo(f"✅ Posted successfully!")
            else:
                click.echo(f"❌ Failed to post response", err=True)
        else:
            click.echo("Cancelled")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command()
@click.option('--market', required=True, help='Market segment')
@click.option('--min-score', type=float, default=0.85, help='Minimum confidence score')
@click.option('--limit', default=5, help='Maximum number to post')
def batch_post(market, min_score, limit):
    """
    Batch approve and post top-scoring leads for a market.
    
    Example:
        python -m backend.cli.main batch-post --market indie_authors --min-score 0.85 --limit 5
    """
    try:
        # Get high-scoring pending questions
        questions = asyncio.run(db_client.get_questions(
            market=market,
            status='pending',
            min_score=min_score,
            limit=limit
        ))
        
        if not questions:
            click.echo(f"No leads found matching criteria")
            return
        
        click.echo(f"\nFound {len(questions)} high-scoring leads")
        click.echo(f"Market: {market}, Min Score: {min_score}\n")
        
        if not click.confirm(f'Proceed to post {len(questions)} responses?'):
            click.echo("Cancelled")
            return
        
        success_count = 0
        for question in questions:
            response = asyncio.run(db_client.get_agent_response(question.id))
            
            if response and response.response_text and not response.posted:
                click.echo(f"Posting: {question.title[:50]}...")
                success = asyncio.run(response_generator.post_response(question, response.response_text))
                
                if success:
                    asyncio.run(db_client.update_response_posted(
                        response.id,
                        posted=True,
                        posted_at=datetime.utcnow()
                    ))
                    success_count += 1
                    click.echo(f"  ✅ Posted")
                else:
                    click.echo(f"  ❌ Failed")
        
        click.echo(f"\nCompleted: {success_count}/{len(questions)} posted successfully\n")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command()
@click.option('--market', required=True, help='Market segment to crawl')
@click.option('--limit', default=100, help='Maximum questions to fetch')
def crawl(market, limit):
    """
    Manually trigger a crawl for a specific market.
    
    Example:
        python -m backend.cli.main crawl --market course_creators
    """
    try:
        click.echo(f"Starting crawl for market '{market}'...")
        
        result = asyncio.run(crawler_manager.crawl_market(market, limit))
        
        click.echo(f"\n{'='*80}")
        click.echo(f"CRAWL RESULTS FOR: {market.upper()}")
        click.echo(f"{'='*80}")
        
        if 'error' in result:
            click.echo(f"Error: {result['error']}", err=True)
        else:
            click.echo(f"Total Found:  {result.get('total_found', 0)}")
            click.echo(f"Total Stored: {result.get('total_stored', 0)}")
            
            if 'platforms' in result:
                click.echo(f"\nPer Platform:")
                for platform_result in result['platforms']:
                    platform = platform_result.get('platform', 'unknown')
                    found = platform_result.get('items_found', 0)
                    stored = platform_result.get('items_stored', 0)
                    click.echo(f"  {platform}: {stored} stored from {found} found")
        
        click.echo(f"{'='*80}\n")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command()
@click.option('--market', help='Filter by market')
@click.option('--days', default=7, help='Number of days to analyze')
def stats(market, days):
    """
    Show analytics and statistics.
    
    Example:
        python -m backend.cli.main stats --market indie_authors --days 7
    """
    try:
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get analytics
        analytics = asyncio.run(db_client.get_analytics(since_date=since, market=market))
        
        click.echo(f"\n{'='*80}")
        click.echo(f"ANALYTICS" + (f" FOR: {market.upper()}" if market else " (ALL MARKETS)"))
        click.echo(f"Period: Last {days} days")
        click.echo(f"{'='*80}\n")
        
        click.echo(f"Total Questions:      {analytics.get('total_questions', 0)}")
        click.echo(f"Total Responses:      {analytics.get('total_responses', 0)}")
        click.echo(f"Success Rate:         {analytics.get('response_success_rate', 0):.1%}")
        click.echo(f"Avg Confidence Score: {analytics.get('avg_confidence_score', 0):.2f}")
        
        if 'questions_by_status' in analytics:
            click.echo(f"\nBy Status:")
            for status, count in analytics['questions_by_status'].items():
                click.echo(f"  {status}: {count}")
        
        if 'questions_by_platform' in analytics:
            click.echo(f"\nBy Platform:")
            for platform, count in analytics['questions_by_platform'].items():
                click.echo(f"  {platform}: {count}")
        
        if 'questions_by_market' in analytics:
            click.echo(f"\nBy Market:")
            for mkt, count in analytics['questions_by_market'].items():
                click.echo(f"  {mkt}: {count}")
        
        click.echo(f"\n{'='*80}\n")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command()
def markets():
    """
    List all configured markets.
    
    Example:
        python -m backend.cli.main markets
    """
    try:
        all_markets = get_all_markets()
        
        click.echo(f"\n{'='*80}")
        click.echo(f"CONFIGURED MARKETS")
        click.echo(f"{'='*80}\n")
        
        for market_name in all_markets:
            config = get_market_config(market_name)
            if config:
                click.echo(f"📊 {market_name}")
                click.echo(f"   Description: {config.description}")
                click.echo(f"   Platforms:   {', '.join(config.platforms)}")
                click.echo(f"   Crawl Interval: Every {config.crawl_interval_hours} hours")
                click.echo(f"   Min Confidence: {config.min_confidence_score}")
                click.echo()
        
        click.echo(f"Total: {len(all_markets)} markets configured\n")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


if __name__ == '__main__':
    cli()

