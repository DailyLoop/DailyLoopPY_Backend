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

# Initialize logger
logger = setup_logger(__name__)

# Configure OpenAI with your API key from environment variables
openai.api_key = Config.OPENAI_API_KEY

# No need to instantiate a client object; we'll use openai.ChatCompletion.create directly.

from supabase import create_client, Client  # Make sure you're using supabase-py or your preferred client

from dotenv import load_dotenv
load_dotenv('../../.env')  # Optional: Only use this for local development.

# Use your service key here for secure server-side operations.
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


@log_exception(logger)
def run_summarization(text):
    """
    Generates a concise summary of the provided text using OpenAI's GPT model.

    Args:
        text (str): The input text to be summarized.

    Returns:
        str: A summarized version of the input text (approximately 150 words).
             Returns an error message if summarization fails.

    Note:
        Uses OpenAI's GPT-4 (or your specified model) with specific parameters:
        - Temperature: 0.5
        - Max tokens: 200
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Change to your desired model (e.g., "gpt-3.5-turbo")
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text in approximately 150 words."},
                {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
            ],
            max_tokens=200,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in summarization: {str(e)}")
        return "Error generating summary"


if __name__ == '__main__':
    process_articles()