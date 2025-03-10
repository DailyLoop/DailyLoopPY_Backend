#!/usr/bin/env python3
"""
Summarization Service Module

This module provides functionality for fetching, processing, and summarizing news articles.
It includes capabilities for content extraction, text summarization, and keyword extraction.

Key Features:
- Article content fetching from URLs
- Text summarization using OpenAI's GPT models
- Keyword extraction using YAKE
- Integration with Supabase for data persistence
"""

import json
import requests
import openai
from backend.core.config import Config
from backend.core.utils import setup_logger, log_exception
import os

# Import the refactored modules
from backend.microservices.summarization.content_fetcher import fetch_article_content
from backend.microservices.summarization.keyword_extractor import get_keywords
from backend.microservices.summarization.article_processor import process_articles
from backend.microservices.summarization.summarization_utils import run_summarization

# Initialize logger
logger = setup_logger(__name__)

# Configure OpenAI with your API key from environment variables
openai.api_key = Config.OPENAI_API_KEY

# No need to instantiate a client object; we'll use openai.ChatCompletion.create directly.

from supabase import create_client, Client  # Make sure you're using supabase-py or your preferred client

from dotenv import load_dotenv
load_dotenv('../../.env')  # Optional: Only use this for local development.

# Use your service key here for secure server-side operations.
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


if __name__ == '__main__':
    process_articles()