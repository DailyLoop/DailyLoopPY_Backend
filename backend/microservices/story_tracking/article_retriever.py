#!/usr/bin/env python3
"""
Article Retriever Module

This module provides functionality for retrieving articles related to tracked stories.
It handles the fetching of article data from the database and manages the relationship
between tracked stories and their associated articles.
"""

import datetime
import logging
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client with service role key for admin access to bypass RLS
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create Supabase client for database operations
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

logger.info("Article Retriever Service initialized with Supabase configuration")

def get_story_articles(story_id):
    """
    Gets all articles related to a tracked story.
    
    Args:
        story_id: The ID of the tracked story
        
    Returns:
        List of articles related to the tracked story
    """
    logger.info(f"Getting articles for story {story_id}")
    try:
        # Get all article IDs related to the tracked story
        result = supabase.table("tracked_story_articles") \
            .select("news_id, added_at") \
            .eq("tracked_story_id", story_id) \
            .order("added_at", desc=True) \
            .execute()
        
        article_refs = result.data if result.data else []
        logger.info(f"Found {len(article_refs)} article references")
        
        if not article_refs:
            return []
        
        # Get the full article details for each article ID
        articles = []
        for ref in article_refs:
            logger.debug(f"Getting details for article {ref['news_id']}")
            article_result = supabase.table("news_articles") \
                .select("*") \
                .eq("id", ref["news_id"]) \
                .execute()
            
            if article_result.data and len(article_result.data) > 0:
                article = article_result.data[0]
                # Add the added_at timestamp from the join table
                article["added_at"] = ref["added_at"]
                articles.append(article)
                logger.debug(f"Added article: {article.get('title', 'No title')}")
            else:
                logger.warning(f"No data found for article {ref['news_id']}")
        
        return articles
    
    except Exception as e:
        logger.error(f"Error getting story articles: {str(e)}")
        raise e