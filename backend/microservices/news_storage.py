# backend/microservices/news_storage.py
"""
News Storage Service - Supabase Database Integration Module

This module provides functions for storing and retrieving news articles and user interactions
with the Supabase database. It handles article storage and imports user search history logging 
and bookmark management operations from dedicated modules.

The module uses the Supabase client to interact with the following tables:
- news_articles: Stores article content and metadata

Other functionality has been moved to dedicated modules:
- User search history: storage/search_logger.py
- Bookmark management: storage/bookmark_service.py

Environment Variables Required:
- VITE_SUPABASE_URL: Supabase project URL
- VITE_SUPABASE_ANON_KEY: Supabase anonymous key for client operations
"""

import os
import datetime
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Import functions from storage modules
from backend.microservices.storage.search_logger import log_user_search
from backend.microservices.storage.bookmark_service import (
    add_bookmark,
    get_user_bookmarks,
    delete_bookmark
)

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv('../../.env')

# Initialize Supabase client with environment variables
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")  # Using anon key for server-side operations
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

logger.info("News Storage Service initialized with Supabase configuration")

def store_article_in_supabase(article):
    """
    Inserts a news article into the Supabase news_articles table if it doesn't already exist.
    
    This function first checks if an article with the same URL already exists in the database.
    If it does, the function returns the existing article's ID. Otherwise, it inserts the new
    article and returns the newly created ID. Uniqueness is enforced by the URL field (which 
    is UNIQUE in the table).
    
    Args:
        article (dict): A dictionary containing article data with the following keys:
            - title (str): The article title
            - summary (str, optional): A summary of the article
            - content (str, optional): The full article content
            - source (dict or str): The source of the article
            - publishedAt (str): Publication date in ISO format
            - url (str): The unique URL to the article
            - urlToImage (str, optional): URL to the article's image
    
    Returns:
        str: The ID of the article (either existing or newly created)
    """
    logger.debug(f"Attempting to store article: {article.get('title')} from {article.get('url')}")
    
    # Check if the article already exists using the URL as unique identifier
    try:
        existing = supabase.table("news_articles").select("*").eq("url", article["url"]).execute()
        if existing.data and len(existing.data) > 0:
            # Article already exists; return its id
            logger.info(f"Article already exists with ID: {existing.data[0]['id']}")
            return existing.data[0]["id"]
        else:
            # Insert a new article with all available fields
            logger.debug("Article not found in database, proceeding with insertion")
            result = supabase.table("news_articles").insert({
                "title": article["title"],
                "summary": article.get("summary", ""),
                "content": article.get("content", ""),
                # Handle source field which can be a dict (from API) or a plain string
                "source": article["source"]["name"] if isinstance(article.get("source"), dict) else article["source"],
                "published_at": article["publishedAt"],
                "url": article["url"],
                "image": article.get("urlToImage", "")
            }).execute()
            logger.info(f"Successfully stored new article with ID: {result.data[0]['id']}")
            return result.data[0]["id"]
    except Exception as e:
        logger.error(f"Error storing article in Supabase: {str(e)}")
        raise

# The functions log_user_search, add_bookmark, get_user_bookmarks, and delete_bookmark
# have been moved to dedicated modules in the storage directory and are now imported above