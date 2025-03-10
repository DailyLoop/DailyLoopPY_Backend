#!/usr/bin/env python3
"""
Bookmark Service Module

This module provides functions for managing user bookmarks in the Supabase database.
It handles creating, retrieving, and deleting bookmark relationships between users and articles.

The module uses the Supabase client to interact with the following tables:
- user_bookmarks: Manages user article bookmarks
- news_articles: Retrieves article data for bookmarks

Environment Variables Required:
- VITE_SUPABASE_URL: Supabase project URL
- VITE_SUPABASE_ANON_KEY: Supabase anonymous key for client operations
"""

import os
import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('../../../.env')

# Initialize Supabase client with environment variables
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")  # Using anon key for server-side operations
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def add_bookmark(user_id, news_id):
    """
    Adds a bookmark by inserting a record into the user_bookmarks table.
    
    This function creates a bookmark relationship between a user and a news article,
    allowing users to save articles for later reading.
    
    Args:
        user_id (str): The ID of the user adding the bookmark
        news_id (str): The ID of the news article to bookmark
    
    Returns:
        dict or None: The created bookmark record if successful, None otherwise
    
    Raises:
        Exception: If there's an error during the database operation
    """
    try:
        # Insert a new bookmark record linking user to article
        result = supabase.table("user_bookmarks").insert({
            "user_id": user_id,
            "news_id": news_id,
        }).execute()
        
        # Return the first data item if available, otherwise None
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error adding bookmark: {str(e)}")
        # Re-raise the exception for proper error handling upstream
        raise e

def get_user_bookmarks(user_id):
    """
    Retrieves all bookmarked articles for a user with full article details.
    
    This function performs a join between the user_bookmarks table and the news_articles table
    to retrieve complete article information for all articles bookmarked by the specified user.
    The results are transformed into a more user-friendly format where each article includes its
    bookmark_id for reference.
    
    Args:
        user_id (str): The ID of the user whose bookmarks should be retrieved
    
    Returns:
        list: A list of dictionaries, each containing the full details of a bookmarked article
              with an additional 'bookmark_id' field
    
    Raises:
        Exception: If there's an error during the database operation
    """
    try:
        # Query user_bookmarks and join with news_articles to get full article details
        # This uses Supabase's foreign key relationships to perform the join
        result = supabase.table("user_bookmarks") \
            .select(
                "id,"
                "news_articles(id,title,summary,content,source,published_at,url,image)"
            ) \
            .eq("user_id", user_id) \
            .execute()
        
        # Transform the nested result structure to a more friendly format
        # by flattening the news_articles data and adding the bookmark_id
        bookmarks = []
        for item in result.data:
            article = item["news_articles"]
            article["bookmark_id"] = item["id"]  # Add bookmark ID to article for reference
            bookmarks.append(article)
            
        return bookmarks
    except Exception as e:
        print(f"Error fetching bookmarks: {str(e)}")
        # Re-raise the exception for proper error handling upstream
        raise e

def delete_bookmark(user_id, bookmark_id):
    """
    Deletes a bookmark from the user_bookmarks table.
    
    This function removes a bookmark relationship between a user and an article.
    It ensures that users can only delete their own bookmarks by checking both the
    bookmark_id and user_id in the query.
    
    Args:
        user_id (str): The ID of the user who owns the bookmark
        bookmark_id (str): The ID of the bookmark to delete
    
    Returns:
        bool: True if the bookmark was successfully deleted, False if no bookmark was found
              or if the deletion was unsuccessful
    
    Raises:
        Exception: If there's an error during the database operation
    """
    try:
        # Delete the bookmark, ensuring it belongs to the specified user
        # This double condition prevents users from deleting other users' bookmarks
        result = supabase.table("user_bookmarks") \
            .delete() \
            .eq("id", bookmark_id) \
            .eq("user_id", user_id) \
            .execute()
        
        # Return True if at least one record was deleted, False otherwise
        return len(result.data) > 0
    except Exception as e:
        print(f"Error deleting bookmark: {str(e)}")
        # Re-raise the exception for proper error handling upstream
        raise e