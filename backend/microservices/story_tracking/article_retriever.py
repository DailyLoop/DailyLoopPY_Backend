#!/usr/bin/env python3
"""
Article Retriever Module

This module provides functionality for retrieving articles related to tracked stories.
It handles the fetching of article data from the database and manages the relationship
between tracked stories and their associated articles.
"""

import datetime
import logging

# Import centralized Supabase client
from backend.core.supabase_client import supabase

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.info("Article Retriever Service initialized with Supabase configuration")

def get_articles_for_stories(story_ids):
    """
    Gets all articles related to multiple tracked stories in a single batch operation.

    Args:
        story_ids: List of story IDs to fetch articles for

    Returns:
        Dict mapping story_id to list of articles
    """
    logger.info(f"Getting articles for {len(story_ids)} stories")
    try:
        if not story_ids:
            return {}

        # Get all article references for all stories in a single query
        result = supabase.table("tracked_story_articles") \
            .select("tracked_story_id, news_id, added_at") \
            .in_("tracked_story_id", story_ids) \
            .order("added_at", desc=True) \
            .execute()

        article_refs = result.data if result.data else []
        logger.info(f"Found {len(article_refs)} article references across {len(story_ids)} stories")

        if not article_refs:
            return {story_id: [] for story_id in story_ids}

        # Collect all unique news IDs and fetch article details in a single batch query
        news_ids = list(set(ref["news_id"] for ref in article_refs))
        logger.debug(f"Fetching details for {len(news_ids)} unique articles")
        articles_result = supabase.table("news_articles") \
            .select("*") \
            .in_("id", news_ids) \
            .execute()

        # Create a lookup dict keyed by article ID
        article_lookup = {}
        if articles_result.data:
            for article in articles_result.data:
                article_lookup[article["id"]] = article

        # Group articles by story_id
        articles_by_story = {story_id: [] for story_id in story_ids}
        for ref in article_refs:
            article = article_lookup.get(ref["news_id"])
            if article:
                # Add the added_at timestamp from the join table
                article["added_at"] = ref["added_at"]
                articles_by_story[ref["tracked_story_id"]].append(article)
            else:
                logger.warning(f"No data found for article {ref['news_id']}")

        return articles_by_story

    except Exception as e:
        logger.error(f"Error getting articles for stories: {str(e)}")
        raise e

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

        # Get the full article details for all articles in a single batch query
        news_ids = [ref["news_id"] for ref in article_refs]
        logger.debug(f"Fetching details for {len(news_ids)} articles")
        articles_result = supabase.table("news_articles") \
            .select("*") \
            .in_("id", news_ids) \
            .execute()

        # Create a lookup dict keyed by article ID
        article_lookup = {}
        if articles_result.data:
            for article in articles_result.data:
                article_lookup[article["id"]] = article

        # Map results to maintain order from article_refs and add timestamps
        articles = []
        for ref in article_refs:
            article = article_lookup.get(ref["news_id"])
            if article:
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