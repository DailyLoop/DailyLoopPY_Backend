#!/usr/bin/env python3
"""
Article Processor Module

This module provides functionality for processing news articles, including:
- Fetching article content
- Generating summaries
- Extracting keywords
- Managing bookmarks

It integrates with Supabase for data persistence and OpenAI for text summarization.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from backend.core.utils import setup_logger, log_exception
from backend.microservices.summarization.content_fetcher import fetch_article_content
from backend.microservices.summarization.keyword_extractor import get_keywords

# Import the summarization function from the main service
# This avoids circular imports while maintaining functionality
from backend.microservices.summarization_service import run_summarization

# Initialize logger
logger = setup_logger(__name__)

# Load environment variables
load_dotenv('../../.env')  # Optional: Only use this for local development

# Initialize Supabase client
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

@log_exception(logger)
def process_articles(article_ids, user_id):
    """
    Processes a batch of articles associated with a specific session ID.
    
    This function performs the following operations:
    1. Retrieves articles from Supabase based on the session ID.
    2. Fetches missing content for articles if needed.
    3. Generates summaries for each article.
    4. Extracts keywords for filtering.
    
    Args:
        article_ids (list): A list of article IDs to process.
        user_id (str): The ID of the user for bookmark checking.

    Returns:
        list: A list of dictionaries containing processed article data.
    """
    try:
        articles = []

        # Step 1: Fetch the news_ids from user_bookmarks for the given user_id
        bookmark_result = supabase.table("user_bookmarks").select("id, news_id").eq("user_id", user_id).execute()

        bookmark_records = {}
        if bookmark_result.data:
            bookmark_records = {item["news_id"]: item["id"] for item in bookmark_result.data}

        bookmarked_news_ids = set(item["news_id"] for item in bookmark_result.data) if bookmark_result.data else set()

        print(f"Bookmarked news IDs: {bookmarked_news_ids}")
        print(f"Article IDs: {article_ids}")

        # Step 2: Fetch all articles from news_articles using the article_ids
        if article_ids:  # Assuming article_ids is defined or fetched earlier
            result = supabase.table("news_articles").select("*").in_("id", article_ids).execute()
            articles = result.data

        # Step 3: Add the 'bookmarked' key to each article
        for article in articles:
            article["bookmarked_id"] = bookmark_records.get(article["id"], None)
      
        print(articles)

        summarized_articles = []
        for article in articles:
            logger.info(f"Processing article: {article['title']}")
            
            content = article.get('content')
            if not content:
                content = fetch_article_content(article['url'])
            
            if content:
                summary = run_summarization(content)
            else:
                summary = run_summarization(article.get('content', ''))
            
            summarized_articles.append({
                'id': article['id'],
                'title': article['title'],
                'author': article.get('author', 'Unknown Author'),
                'source': article.get('source'),
                'publishedAt': article.get('published_at'),
                'url': article['url'],
                'urlToImage': article.get('image'),
                'content': article.get('content', ''),
                'summary': summary,
                'filter_keywords': get_keywords(article.get('content', '')),
                'bookmarked_id': article.get('bookmarked_id', None)
            })

        return summarized_articles

    except Exception as e:
        logger.error(f"Error processing articles: {str(e)}")
        raise e