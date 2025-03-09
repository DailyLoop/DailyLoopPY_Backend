#!/usr/bin/env python3
"""
Content Fetcher Module

This module provides functionality for fetching and extracting content from news article URLs.
It handles various HTTP request exceptions and content parsing.
"""

import requests
from bs4 import BeautifulSoup
from backend.core.utils import setup_logger, log_exception

# Initialize logger
logger = setup_logger(__name__)

@log_exception(logger)
def fetch_article_content(url):
    """
    Fetches and extracts the main content from a given URL.

    Args:
        url (str): The URL of the article to fetch content from.

    Returns:
        str or None: The extracted article content as plain text.
                    Returns None if the fetch fails or content is invalid.
    """
    try:
        if not url or not url.startswith('http'):
            logger.error(f"Invalid URL format: {url}")
            return None

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        
        if not paragraphs:
            logger.warning(f"No content found at URL: {url}")
            return None
            
        content = ' '.join([p.get_text() for p in paragraphs])
        return content
        
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out for URL: {url}")
        return None
    except requests.exceptions.SSLError:
        logger.error(f"SSL verification failed for URL: {url}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"Failed to connect to URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching article content from {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing {url}: {str(e)}")
        return None