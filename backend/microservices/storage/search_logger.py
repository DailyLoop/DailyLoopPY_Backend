#!/usr/bin/env python3
"""
Search Logger Module

This module provides functionality for logging user search and article view events.
It records user interactions with news articles for analytics and personalization purposes.

The module uses the Supabase client to interact with the following tables:
- user_search_history: Tracks user search and article view interactions

Environment Variables Required:
- SUPABASE_URL: Supabase project URL
- SUPABASE_SERVICE_ROLE_KEY: Service role key for admin operations
"""

import datetime
import logging

# Import centralized Supabase client
from backend.core.supabase_client import supabase

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.info("Search Logger Service initialized with Supabase configuration")

def log_user_search(user_id, news_id, session_id):
    """
    Logs a search event by inserting a record into the user_search_history join table.
    
    This function creates a record of a user viewing or searching for a specific article,
    which can be used for analytics, personalization, and tracking user activity across sessions.
    
    Args:
        user_id (str): The ID of the user performing the search
        news_id (str): The ID of the news article that was viewed/searched
        session_id (str): The current session identifier for tracking user activity
    
    Returns:
        dict: The Supabase response object containing the result of the insert operation
    """
    logger.info(f"Logging search event for user {user_id}, article {news_id}, session {session_id}")
    try:
        # Create a timestamp for when the search occurred
        current_time = datetime.datetime.utcnow().isoformat()
        
        # Insert the search record with all required fields
        result = supabase.table("user_search_history").insert({
            "user_id": user_id,
            "news_id": news_id,
            "searched_at": current_time,
            "session_id": session_id,
        }).execute()
        logger.debug(f"Search event logged successfully")
        return result
    except Exception as e:
        logger.error(f"Error logging search event: {str(e)}")
        raise e