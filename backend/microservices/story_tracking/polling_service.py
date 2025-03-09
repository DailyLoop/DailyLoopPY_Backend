#!/usr/bin/env python3
"""
Polling Service Module

This module provides functionality for managing polling of tracked stories.
It handles enabling/disabling polling for stories and updating stories with new articles.
"""

import datetime
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from backend.microservices.story_tracking.article_matcher import find_related_articles

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client with service role key for admin access to bypass RLS
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create Supabase client for database operations
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def toggle_polling(user_id, story_id, enable=True):
    """
    Enables or disables polling for a tracked story.
    
    Args:
        user_id: The ID of the user
        story_id: The ID of the tracked story
        enable: True to enable polling, False to disable
        
    Returns:
        The updated tracked story record, or None if the story wasn't found
    """
    print(f"[DEBUG] [story_tracking_service] [toggle_polling] {'Enabling' if enable else 'Disabling'} polling for story {story_id}, user {user_id}")
    try:
        # Verify that the story belongs to the user
        story_result = supabase.table("tracked_stories") \
            .select("*") \
            .eq("id", story_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not story_result.data or len(story_result.data) == 0:
            print(f"[DEBUG] [story_tracking_service] [toggle_polling] No story found with ID {story_id} for user {user_id}")
            return None
        
        current_time = datetime.datetime.utcnow().isoformat()
        
        # Update the story's polling status
        update_data = {
            "is_polling": enable
        }
        
        # If enabling polling, also set the last_polled_at timestamp
        if enable:
            update_data["last_polled_at"] = current_time
        
        result = supabase.table("tracked_stories") \
            .update(update_data) \
            .eq("id", story_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not result.data or len(result.data) == 0:
            print(f"[DEBUG] [story_tracking_service] [toggle_polling] Failed to update polling status for story {story_id}")
            return None
        
        updated_story = result.data[0]
        print(f"[DEBUG] [story_tracking_service] [toggle_polling] Successfully {'enabled' if enable else 'disabled'} polling for story {story_id}")
        
        # If polling was enabled, fetch articles immediately
        if enable:
            print(f"[DEBUG] [story_tracking_service] [toggle_polling] Performing initial article fetch for newly enabled polling")
            find_related_articles(story_id, updated_story["keyword"])
        
        return updated_story
    
    except Exception as e:
        print(f"[DEBUG] [story_tracking_service] [toggle_polling] Error toggling polling status: {str(e)}")
        raise e

def get_polling_stories():
    """
    Gets all tracked stories that have polling enabled.
    
    This function is intended to be called by the polling worker to fetch
    all stories that need to be checked for updates.
    
    Returns:
        List of tracked stories with polling enabled
    """
    print(f"[DEBUG] [story_tracking_service] [get_polling_stories] Getting all stories with polling enabled")
    try:
        result = supabase.table("tracked_stories") \
            .select("*") \
            .eq("is_polling", True) \
            .execute()
        
        stories = result.data if result.data else []
        print(f"[DEBUG] [story_tracking_service] [get_polling_stories] Found {len(stories)} stories with polling enabled")
        return stories
    
    except Exception as e:
        print(f"[DEBUG] [story_tracking_service] [get_polling_stories] Error getting polling stories: {str(e)}")
        raise e

def update_polling_timestamp(story_id):
    """
    Updates the last_polled_at timestamp for a tracked story.
    
    This function is intended to be called after polling for new articles
    for a story, whether or not new articles were found.
    
    Args:
        story_id: The ID of the tracked story
        
    Returns:
        True if successful, False otherwise
    """
    print(f"[DEBUG] [story_tracking_service] [update_polling_timestamp] Updating polling timestamp for story {story_id}")
    try:
        current_time = datetime.datetime.utcnow().isoformat()
        
        result = supabase.table("tracked_stories") \
            .update({"last_polled_at": current_time}) \
            .eq("id", story_id) \
            .execute()
        
        success = result.data and len(result.data) > 0
        print(f"[DEBUG] [story_tracking_service] [update_polling_timestamp] Update {'successful' if success else 'failed'}")
        return success
    
    except Exception as e:
        print(f"[DEBUG] [story_tracking_service] [update_polling_timestamp] Error updating polling timestamp: {str(e)}")
        return False

def update_polling_stories():
    """
    Update all tracked stories with polling enabled.
    
    This function is similar to update_all_tracked_stories() but focuses only
    on stories with polling enabled. It's intended to be called by the
    polling worker to periodically fetch new articles for active stories.
    
    Returns:
        dict: A dictionary containing statistics about the update operation:
              - stories_updated: Number of stories that received new articles
              - new_articles: Total number of new articles added across all stories
    """
    print(f"[DEBUG] [story_tracking_service] [update_polling_stories] Starting update of polling-enabled stories")
    try:
        # Get all stories with polling enabled
        stories = get_polling_stories()
        
        if not stories:
            print(f"[DEBUG] [story_tracking_service] [update_polling_stories] No polling-enabled stories found")
            return {"stories_updated": 0, "new_articles": 0}
        
        # Update each story
        stories_updated = 0
        total_new_articles = 0
        
        for story in stories:
            story_id = story["id"]
            keyword = story["keyword"]
            print(f"[DEBUG] [story_tracking_service] [update_polling_stories] Polling story {story_id}, keyword: '{keyword}'")
            
            # Find new articles for this story
            new_articles = find_related_articles(story_id, keyword)
            
            # Always update the last_polled_at timestamp, even if no new articles were found
            update_polling_timestamp(story_id)
            
            if new_articles > 0:
                stories_updated += 1
                total_new_articles += new_articles
                print(f"[DEBUG] [story_tracking_service] [update_polling_stories] Added {new_articles} new articles to story {story_id}")
            else:
                print(f"[DEBUG] [story_tracking_service] [update_polling_stories] No new articles found for story {story_id}")
        
        print(f"[DEBUG] [story_tracking_service] [update_polling_stories] Update complete. Updated {stories_updated} stories with {total_new_articles} new articles")
        return {
            "stories_updated": stories_updated,
            "new_articles": total_new_articles
        }
    
    except Exception as e:
        print(f"[DEBUG] [story_tracking_service] [update_polling_stories] Error updating polling stories: {str(e)}")
        raise e