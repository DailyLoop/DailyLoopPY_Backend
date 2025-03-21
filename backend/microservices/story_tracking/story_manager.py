#!/usr/bin/env python3
"""
Story Manager Module

This module provides functionality for managing tracked stories, including:
- Creating new tracked stories
- Retrieving tracked stories for a user
- Getting details for a specific story
- Deleting tracked stories

It integrates with Supabase for data persistence and handles the core story management operations.
"""

import datetime
import logging
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from backend.microservices.story_tracking.article_retriever import get_story_articles
from backend.microservices.story_tracking.article_matcher import find_related_articles

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

logger.info("Story Manager Service initialized with Supabase configuration")

def create_tracked_story(user_id, keyword, source_article_id=None, enable_polling=False):
    """
    Creates a new tracked story for a user based on a keyword.
    
    Args:
        user_id: The ID of the user tracking the story
        keyword: The keyword/topic to track
        source_article_id: Optional ID of the source article that initiated tracking
        enable_polling: Whether to enable automatic polling for this story
        
    Returns:
        The created tracked story record
    """
    
    logger.info(f"Creating tracked story for user {user_id}, keyword: '{keyword}', source_article: {source_article_id}, polling: {enable_polling}")
    try:
        # Check if the user is already tracking this keyword
        logger.debug(f"Checking if user already tracks keyword '{keyword}'")
        existing = supabase.table("tracked_stories") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("keyword", keyword) \
            .execute()
            
        if existing.data and len(existing.data) > 0:
            # User is already tracking this keyword
            logger.info(f"User already tracking this keyword, found {len(existing.data)} existing entries")
            return existing.data[0]
        
        # Create a new tracked story
        logger.debug("Creating new tracked story record")
        current_time = datetime.datetime.utcnow().isoformat()
        result = supabase.table("tracked_stories").insert({
            "user_id": user_id,
            "keyword": keyword,
            "created_at": current_time,
            "last_updated": current_time,
            "is_polling": enable_polling,
            "last_polled_at": current_time if enable_polling else None
        }).execute()
        
        if not result.data:
            logger.error(f"Failed to create tracked story: {result}")
            return None
            
        tracked_story = result.data[0] if result.data else None
        logger.info(f"Tracked story created with ID: {tracked_story['id'] if tracked_story else None}")
        
        # If a source article was provided, link it to the tracked story
        if tracked_story and source_article_id:
            logger.debug(f"Linking source article {source_article_id} to tracked story")
            supabase.table("tracked_story_articles").insert({
                "tracked_story_id": tracked_story["id"],
                "news_id": source_article_id,
                "added_at": datetime.datetime.utcnow().isoformat()
            }).execute()
        
        # Log that we're skipping synchronous article fetching
        logger.debug("Skipping synchronous article fetching to avoid resource contention")
        find_related_articles(tracked_story["id"], keyword)
        
        return tracked_story
    
    except Exception as e:
        logger.error(f"Error creating tracked story: {str(e)}")
        raise e

def get_tracked_stories(user_id):
    """
    Gets all tracked stories for a user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        List of tracked stories with their related articles
    """
    logger.info(f"Getting tracked stories for user {user_id}")
    try:
        # Get all tracked stories for the user
        result = supabase.table("tracked_stories") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()
        
        tracked_stories = result.data if result.data else []
        logger.info(f"Found {len(tracked_stories)} tracked stories")
        
        # For each tracked story, get its related articles
        for story in tracked_stories:
            logger.debug(f"Getting articles for story {story['id']}")
            story["articles"] = get_story_articles(story["id"])
            logger.debug(f"Found {len(story['articles'])} articles for story {story['id']}")
        
        return tracked_stories
    
    except Exception as e:
        logger.error(f"Error getting tracked stories: {str(e)}")
        raise e

def get_story_details(story_id):
    """
    Gets details for a specific tracked story including related articles.
    
    Args:
        story_id: The ID of the tracked story
        
    Returns:
        The tracked story with its related articles
    """
    logger.info(f"Getting story details for story ID {story_id}")
    try:
        # Get the tracked story
        result = supabase.table("tracked_stories") \
            .select("*") \
            .eq("id", story_id) \
            .execute()
        
        if not result.data or len(result.data) == 0:
            logger.warning(f"No story found with ID {story_id}")
            return None
        
        story = result.data[0]
        logger.debug(f"Found story: {story['keyword']}")
        
        # Get related articles
        logger.debug("Getting related articles")
        story["articles"] = get_story_articles(story_id)
        logger.info(f"Found {len(story['articles'])} related articles")
        
        return story
    
    except Exception as e:
        logger.error(f"Error getting story details: {str(e)}")
        raise e

def delete_tracked_story(user_id, story_id):
    """
    Deletes a tracked story for a user.
    
    Args:
        user_id: The ID of the user
        story_id: The ID of the tracked story to delete
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Deleting tracked story {story_id} for user {user_id}")
    try:
        # Delete the tracked story (related articles will be deleted via CASCADE)
        result = supabase.table("tracked_stories") \
            .delete() \
            .eq("id", story_id) \
            .eq("user_id", user_id) \
            .execute()
        
        success = len(result.data) > 0
        logger.info(f"Delete operation {'successful' if success else 'failed'}")
        return success
    
    except Exception as e:
        logger.error(f"Error deleting tracked story: {str(e)}")
        raise e

def update_all_tracked_stories():
    """
    Background job to update all tracked stories with new related articles.
    
    This function is designed to be run as a scheduled task to keep all tracked stories
    up-to-date with the latest news articles. It iterates through all tracked stories in the
    database and calls find_related_articles() for each one to fetch and link new articles.
    
    Returns:
        dict: A dictionary containing statistics about the update operation:
              - stories_updated: Number of stories that received new articles
              - new_articles: Total number of new articles added across all stories
    """
    logger.info("Starting update of all tracked stories")
    try:
        # Get all tracked stories
        result = supabase.table("tracked_stories") \
            .select("id, keyword") \
            .execute()
        
        tracked_stories = result.data if result.data else []
        logger.info(f"Found {len(tracked_stories)} tracked stories to update")
        
        if not tracked_stories:
            return {"stories_updated": 0, "new_articles": 0}
        
        # Update each tracked story
        stories_updated = 0
        total_new_articles = 0
        
        for story in tracked_stories:
            logger.debug(f"Updating story {story['id']}, keyword: '{story['keyword']}'")
            new_articles = find_related_articles(story["id"], story["keyword"])
            if new_articles > 0:
                stories_updated += 1
                total_new_articles += new_articles
                logger.debug(f"Added {new_articles} new articles to story {story['id']}")
            else:
                logger.debug(f"No new articles found for story {story['id']}")
        
        logger.info(f"Update complete. Updated {stories_updated} stories with {total_new_articles} new articles")
        return {
            "stories_updated": stories_updated,
            "new_articles": total_new_articles
        }
    
    except Exception as e:
        logger.error(f"Error updating tracked stories: {str(e)}")
        raise e