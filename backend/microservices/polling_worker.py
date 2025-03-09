#!/usr/bin/env python3
"""
polling_worker.py - Worker for automatic news article polling

This script runs as a background process or scheduled task that periodically:
1. Queries Supabase for tracked stories with polling enabled
2. Fetches new articles for each story's keyword
3. Stores new articles and links them to the tracked story
4. Updates the last_polled_at timestamp

Usage:
- Run directly: python polling_worker.py
- Schedule with cron or a process manager

Environment Variables Required:
- VITE_SUPABASE_URL: Supabase project URL
- SUPABASE_SERVICE_ROLE_KEY: Service role key for admin access
- NEWS_API_KEY: API key for the news service
- POLLING_INTERVAL: Time in minutes between polling cycles (default: 5)
"""

import os
import time
import datetime
import schedule
import logging
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [polling_worker] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
logger.info("Environment variables loaded")

# Initialize Supabase client with service role key for admin access
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL", "5"))  # Default to 5 minutes if not specified

logger.info(f"Supabase URL: {SUPABASE_URL}")
logger.info(f"Supabase Key: {SUPABASE_SERVICE_KEY[:5]}..." if SUPABASE_SERVICE_KEY else "Supabase Key: None")
logger.info(f"News API Key: {NEWS_API_KEY[:5]}..." if NEWS_API_KEY else "News API Key: None")
logger.info(f"Polling interval: {POLLING_INTERVAL} minutes")

# Create Supabase client for database operations
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
logger.info("Supabase client initialized")

def get_active_polling_stories():
    """
    Fetches all stories that have polling enabled
    
    Returns:
        list: Stories with polling enabled, each containing id, user_id, keyword, and last_polled_at
    """
    try:
        logger.info("Fetching active polling stories")
        result = supabase.table("tracked_stories") \
            .select("id, user_id, keyword, last_polled_at") \
            .eq("is_polling", True) \
            .execute()
        
        stories = result.data if result.data else []
        logger.info(f"Found {len(stories)} stories with polling enabled")
        return stories
    except Exception as e:
        logger.error(f"Error fetching polling stories: {str(e)}")
        return []

def fetch_news_articles(keyword, since_date=None):
    """
    Fetches news articles from the News API based on a keyword
    
    Args:
        keyword (str): The search term to find relevant articles
        since_date (str, optional): ISO format date to fetch articles published since then
        
    Returns:
        list: A list of article dictionaries
    """
    try:
        logger.info(f"Fetching news articles for keyword: '{keyword}'")
        
        # Configure the News API endpoint and request parameters
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': keyword,
            'apiKey': NEWS_API_KEY,
            'pageSize': 10,  # Limit results to avoid rate limiting
            'language': 'en',  # English articles only
            'sortBy': 'publishedAt'  # Get newest articles first
        }
        
        # If we have a since_date, add it to the parameters
        if since_date:
            # Format date for News API (YYYY-MM-DD)
            if isinstance(since_date, str):
                try:
                    dt = datetime.datetime.fromisoformat(since_date.replace('Z', '+00:00'))
                    from_date = dt.strftime('%Y-%m-%d')
                    params['from'] = from_date
                except ValueError:
                    logger.warning(f"Invalid date format: {since_date}, skipping date filter")
        
        logger.info(f"Requesting articles with params: {params}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        news_data = response.json()
        if news_data.get('status') == 'ok':
            articles = news_data.get('articles', [])
            logger.info(f"Received {len(articles)} articles from News API")
            return articles
        else:
            logger.error(f"News API error: {news_data.get('message')}")
            return []
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news: {str(e)}")
        return []

def store_article(article):
    """
    Stores an article in the news_articles table if it doesn't exist
    
    Args:
        article (dict): Article data from News API
        
    Returns:
        str: ID of the article in the database, or None if storage failed
    """
    try:
        # Check if article with same URL already exists
        url = article.get('url')
        if not url:
            logger.warning("Article missing URL, skipping")
            return None
            
        logger.info(f"Checking if article exists: {url}")
        result = supabase.table("news_articles") \
            .select("id") \
            .eq("url", url) \
            .execute()
            
        if result.data and len(result.data) > 0:
            logger.info(f"Article already exists with ID: {result.data[0]['id']}")
            return result.data[0]['id']
        
        # Prepare article data
        source = article.get('source', {}).get('name', 'Unknown Source')
        publish_date = article.get('publishedAt', datetime.datetime.utcnow().isoformat())
        
        new_article = {
            "title": article.get('title', 'No Title'),
            "content": article.get('content', article.get('description', 'No Content')),
            "summary": article.get('description', 'No Summary'),
            "source": source,
            "url": url,
            "urlToImage": article.get('urlToImage', ''),
            "author": article.get('author', 'Unknown'),
            "publishedAt": publish_date
        }
        
        # Insert article into news_articles table
        logger.info(f"Storing new article: {new_article['title'][:30]}...")
        result = supabase.table("news_articles").insert(new_article).execute()
        
        if result.data and len(result.data) > 0:
            article_id = result.data[0]['id']
            logger.info(f"Article stored with ID: {article_id}")
            return article_id
        else:
            logger.error("Failed to store article")
            return None
            
    except Exception as e:
        logger.error(f"Error storing article: {str(e)}")
        return None

def link_article_to_story(story_id, article_id):
    """
    Links an article to a tracked story in the tracked_story_articles table
    
    Args:
        story_id (str): ID of the tracked story
        article_id (str): ID of the article
        
    Returns:
        bool: True if linking was successful, False otherwise
    """
    try:
        # Check if link already exists
        result = supabase.table("tracked_story_articles") \
            .select("*") \
            .eq("tracked_story_id", story_id) \
            .eq("news_id", article_id) \
            .execute()
            
        if result.data and len(result.data) > 0:
            logger.info(f"Article {article_id} already linked to story {story_id}")
            return True
            
        # Create new link
        logger.info(f"Linking article {article_id} to story {story_id}")
        result = supabase.table("tracked_story_articles").insert({
            "tracked_story_id": story_id,
            "news_id": article_id,
            "added_at": datetime.datetime.utcnow().isoformat()
        }).execute()
        
        if result.data and len(result.data) > 0:
            logger.info("Article linked successfully")
            return True
        else:
            logger.error("Failed to link article to story")
            return False
            
    except Exception as e:
        logger.error(f"Error linking article to story: {str(e)}")
        return False

def update_story_timestamps(story_id, has_new_articles=False):
    """
    Updates the last_polled_at timestamp for a story and last_updated if new articles were found
    
    Args:
        story_id (str): ID of the tracked story
        has_new_articles (bool): Whether new articles were found
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        current_time = datetime.datetime.utcnow().isoformat()
        update_data = {
            "last_polled_at": current_time
        }
        
        # Only update last_updated if new articles were found
        if has_new_articles:
            update_data["last_updated"] = current_time
            
        logger.info(f"Updating timestamps for story {story_id}")
        result = supabase.table("tracked_stories") \
            .update(update_data) \
            .eq("id", story_id) \
            .execute()
            
        if result.data and len(result.data) > 0:
            logger.info("Timestamps updated successfully")
            return True
        else:
            logger.error("Failed to update timestamps")
            return False
            
    except Exception as e:
        logger.error(f"Error updating timestamps: {str(e)}")
        return False

def poll_story(story):
    """
    Polls for new articles for a specific story
    
    Args:
        story (dict): Story object with id, keyword and last_polled_at
        
    Returns:
        int: Number of new articles found
    """
    try:
        story_id = story["id"]
        keyword = story["keyword"]
        last_polled_at = story.get("last_polled_at")
        
        logger.info(f"Polling story {story_id} with keyword: '{keyword}'")
        
        # Fetch articles from News API
        articles = fetch_news_articles(keyword, last_polled_at)
        
        if not articles:
            logger.info(f"No new articles found for keyword: '{keyword}'")
            update_story_timestamps(story_id, False)
            return 0
            
        # Process each article and store it
        new_articles_count = 0
        
        for article in articles:
            # Store article in news_articles table
            article_id = store_article(article)
            
            if article_id:
                # Link the article to the tracked story
                success = link_article_to_story(story_id, article_id)
                if success:
                    new_articles_count += 1
        
        # Update the story timestamps
        update_story_timestamps(story_id, new_articles_count > 0)
        
        logger.info(f"Poll complete for story {story_id}. Found {new_articles_count} new articles")
        return new_articles_count
    
    except Exception as e:
        logger.error(f"Error polling story {story.get('id', 'unknown')}: {str(e)}")
        # Still try to update last_polled_at even if there was an error
        try:
            update_story_timestamps(story.get('id'), False)
        except:
            pass
        return 0

def run_polling_cycle():
    """
    Main function to run a complete polling cycle for all active stories
    """
    logger.info("Starting polling cycle")
    start_time = time.time()
    
    try:
        stories = get_active_polling_stories()
        if not stories:
            logger.info("No active polling stories found. Polling cycle complete.")
            return
        
        total_new_articles = 0
        stories_updated = 0
        
        for story in stories:
            try:
                # Skip stories polled very recently (within last minute) to avoid redundant polls
                if story.get("last_polled_at"):
                    last_polled = datetime.datetime.fromisoformat(story["last_polled_at"].replace('Z', '+00:00'))
                    now = datetime.datetime.utcnow()
                    time_since_last_poll = (now - last_polled).total_seconds() / 60  # in minutes
                    
                    if time_since_last_poll < 1:  # Less than 1 minute
                        logger.info(f"Skipping story {story['id']} - polled recently ({time_since_last_poll:.1f} minutes ago)")
                        continue
                
                new_articles = poll_story(story)
                if new_articles > 0:
                    total_new_articles += new_articles
                    stories_updated += 1
            except Exception as e:
                logger.error(f"Error processing story {story.get('id', 'unknown')}: {str(e)}")
                # Continue with next story
        
        elapsed_time = time.time() - start_time
        logger.info(f"Polling cycle complete. Updated {stories_updated} stories with {total_new_articles} new articles in {elapsed_time:.2f} seconds")
    
    except Exception as e:
        logger.error(f"Error in polling cycle: {str(e)}")

def start_scheduled_polling():
    """
    Starts the scheduler to run polling at regular intervals
    """
    logger.info(f"Setting up scheduled polling every {POLLING_INTERVAL} minutes")
    
    # Run immediately when started
    run_polling_cycle()
    
    # Schedule regular polling
    schedule.every(POLLING_INTERVAL).minutes.do(run_polling_cycle)
    
    logger.info("Polling scheduler started")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logger.info("Polling worker starting up")
    try:
        start_scheduled_polling()
    except KeyboardInterrupt:
        logger.info("Polling worker shutting down")
    except Exception as e:
        logger.error(f"Unexpected error in polling worker: {str(e)}")