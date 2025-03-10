#!/usr/bin/env python3
"""
Search Logger Module

This module provides functionality for logging user search and article view events.
It records user interactions with news articles for analytics and personalization purposes.

The module uses the Supabase client to interact with the following tables:
- user_search_history: Tracks user search and article view interactions

Environment Variables Required:
- VITE_SUPABASE_URL: Supabase project URL
- VITE_SUPABASE_ANON_KEY: Supabase anonymous key for client operations
"""

import os
import datetime
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv('../../../.env')

# Initialize Supabase client with environment variables
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")  # Using anon key for server-side operations
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

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