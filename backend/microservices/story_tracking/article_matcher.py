#!/usr/bin/env python3
"""
Article Matcher Module

This module provides functionality for finding and matching articles related to tracked stories.
It integrates with the news fetcher service to find relevant articles based on keywords.
"""

import datetime
import logging
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from backend.microservices.news_fetcher import fetch_news
from backend.microservices.news_storage import store_article_in_supabase

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client with service role key for admin access to bypass RLS
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Create Supabase client for database operations
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

logger.info("Article Matcher Service initialized with Supabase configuration")

def find_related_articles(story_id, keyword):
    """
    Finds and adds articles related to a tracked story based on its keyword.
    
    Args:
        story_id: The ID of the tracked story
        keyword: The keyword to search for
        
    Returns:
        Number of new articles added
    """
    logger.info(f"Finding related articles for story {story_id}, keyword: '{keyword}'")
    try:
        # Get the tracked story to check when it was last updated
        story_result = supabase.table("tracked_stories") \
            .select("*") \
            .eq("id", story_id) \
            .execute()
        
        if not story_result.data or len(story_result.data) == 0:
            logger.warning(f"No story found with ID {story_id}")
            return 0
        
        story = story_result.data[0]
        logger.debug(f"Found story: {story['keyword']}")
        
        # Fetch articles related to the keyword
        logger.info(f"Fetching articles for keyword '{keyword}'")
        articles = fetch_news(keyword)
        
        if not articles:
            logger.info(f"No articles found for keyword '{keyword}'")
            return 0
        
        logger.info(f"Found {len(articles)} articles for keyword '{keyword}'")
        
        # Get existing article IDs for this story to avoid duplicates
        logger.debug(f"Getting existing article IDs for story {story_id}")
        existing_result = supabase.table("tracked_story_articles") \
            .select("news_id") \
            .eq("tracked_story_id", story_id) \
            .execute()
        
        existing_ids = [item["news_id"] for item in existing_result.data] if existing_result.data else []
        logger.debug(f"Found {len(existing_ids)} existing article IDs")
        
        # Process and add new articles
        new_articles_count = 0
        for article in articles:
            # First, store the article in the news_articles table
            logger.debug(f"Storing article: {article.get('title', 'No title')}")
            article_id = store_article_in_supabase(article)
            logger.debug(f"Article stored with ID: {article_id}")
            
            # If this article is not already linked to the story, add it
            if article_id not in existing_ids:
                logger.debug(f"Linking new article {article_id} to story {story_id}")
                supabase.table("tracked_story_articles").insert({
                    "tracked_story_id": story_id,
                    "news_id": article_id,
                    "added_at": datetime.datetime.utcnow().isoformat()
                }).execute()
                new_articles_count += 1
            else:
                logger.debug(f"Article {article_id} already linked to story")
        
        logger.info(f"Added {new_articles_count} new articles to story {story_id}")
        
        # Update the last_updated timestamp of the tracked story
        if new_articles_count > 0:
            logger.debug(f"Updating last_updated timestamp for story {story_id}")
            supabase.table("tracked_stories") \
                .update({"last_updated": datetime.datetime.utcnow().isoformat()}) \
                .eq("id", story_id) \
                .execute()
        
        return new_articles_count
    
    except Exception as e:
        logger.error(f"Error finding related articles: {str(e)}")
        raise e