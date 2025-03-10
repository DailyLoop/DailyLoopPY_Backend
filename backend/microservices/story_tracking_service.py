#!/usr/bin/env python3
"""
story_tracking_service.py - Microservice for Story Tracking

This service provides functionality for tracking news stories by keyword and finding related articles.
It integrates with Supabase for data persistence and manages user story tracking preferences.

Key Features:
- Story tracking by keywords
- Related article discovery
- User story management
- Automatic story updates
- Polling for new articles

The service uses clustering algorithms to group similar articles and maintains
relationships between tracked stories and their associated articles.

Database Tables Used:
- tracked_stories: Stores user story tracking preferences
- tracked_story_articles: Links stories to their related articles
- news_articles: Stores article content and metadata

Environment Variables Required:
- SUPABASE_URL: Supabase project URL
- SUPABASE_ANON_KEY: Service role key for admin access
"""

#TODO: Implement proper background processing: Use a task queue like Celery to handle article fetching in the background

import os
import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
# from summarization.story_tracking.story_tracking import cluster_articles
from backend.microservices.news_fetcher import fetch_news

# Import the refactored modules
from backend.microservices.story_tracking.article_matcher import find_related_articles
from backend.microservices.story_tracking.polling_service import (
    toggle_polling,
    get_polling_stories,
    update_polling_timestamp,
    update_polling_stories
)
from backend.microservices.story_tracking.story_manager import (
    create_tracked_story,
    get_tracked_stories,
    get_story_details,
    delete_tracked_story,
    update_all_tracked_stories
)
from backend.microservices.story_tracking.article_retriever import get_story_articles

# Service initialization logging
print("[DEBUG] [story_tracking_service] [main] Story tracking service starting...")

# Load environment variables from .env file
load_dotenv()
print("[DEBUG] [story_tracking_service] [main] Environment variables loaded")

# Initialize Supabase client with service role key for admin access to bypass RLS
# RLS (Row Level Security) policies are bypassed when using the service role key
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

print(f"[DEBUG] [story_tracking_service] [main] Supabase URL: {SUPABASE_URL}")
print(f"[DEBUG] [story_tracking_service] [main] Supabase Key: {SUPABASE_ANON_KEY[:5]}..." if SUPABASE_ANON_KEY else "[DEBUG] [story_tracking_service] [main] Supabase Key: None")

# Create Supabase client for database operations
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

print("[DEBUG] [story_tracking_service] [main] Supabase client initialized")

def run_story_tracking(article_embeddings):
    """
    Runs the story tracking algorithm on a set of article embeddings to identify story clusters.
    
    This function uses clustering algorithms to group similar articles together based on their
    vector embeddings, helping to identify distinct news stories or topics.
    
    Args:
        article_embeddings: List of vector embeddings for articles. Each embedding should be
                          a numerical vector representing the article's content.
                          
    Returns:
        list: A list of cluster labels indicating which story cluster each article belongs to.
              Empty list is returned if article_embeddings is None or empty.
    """
    print(f"[DEBUG] [story_tracking_service] [run_story_tracking] Running story tracking with {len(article_embeddings) if article_embeddings else 0} embeddings")
    # Uncomment when clustering functionality is implemented
    # labels = cluster_articles(article_embeddings)
    # print(f"[DEBUG] [story_tracking_service] [run_story_tracking] Clustering complete, found {len(labels) if labels else 0} labels")
    # return labels
    return []

# update_polling_stories function has been moved to backend.microservices.story_tracking.polling_service
# update_all_tracked_stories function has been moved to backend.microservices.story_tracking.story_manager

if __name__ == '__main__':
    # Example usage - this code runs when the script is executed directly
    print("[DEBUG] [story_tracking_service] [main] Running story_tracking_service.py as main")
    result = update_all_tracked_stories()
    print(f"[DEBUG] [story_tracking_service] [main] Updated {result['stories_updated']} stories with {result['new_articles']} new articles")
    print("[DEBUG] [story_tracking_service] [main] Execution completed")
