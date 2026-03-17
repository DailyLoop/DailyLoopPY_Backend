#!/usr/bin/env python3
"""
Summarization Service Module

This module provides functionality for fetching, processing, and summarizing news articles.
It includes capabilities for content extraction, text summarization, and keyword extraction.

Key Features:
- Article content fetching from URLs
- Text summarization using Google Gemini API
- Keyword extraction using YAKE
- Integration with Supabase for data persistence
"""

import google.generativeai as genai
from backend.core.config import Config
from backend.core.utils import setup_logger, log_exception

# Import the refactored modules
from backend.microservices.summarization.content_fetcher import fetch_article_content
from backend.microservices.summarization.keyword_extractor import get_keywords
from backend.microservices.summarization.article_processor import process_articles
from backend.microservices.summarization.summarization_utils import run_summarization

# Initialize logger
logger = setup_logger(__name__)

# Configure Gemini with your API key from environment variables
genai.configure(api_key=Config.GEMINI_API_KEY)


if __name__ == '__main__':
    # Example usage: process_articles(article_ids=['<article_id>'], user_id='<user_id>')
    logger.info("Summarization service module loaded")