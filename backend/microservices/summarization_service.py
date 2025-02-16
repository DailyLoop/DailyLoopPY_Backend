#!/usr/bin/env python3
"""
summarization_service.py - Microservice for Summarization
"""

import json
import requests
import time
from bs4 import BeautifulSoup
from openai import OpenAI
from backend.core.config import Config
from backend.core.utils import setup_logger, log_exception

# Initialize logger
logger = setup_logger(__name__)

# Configure OpenAI
client = OpenAI(api_key=Config.OPENAI_API_KEY)

@log_exception(logger)
def fetch_article_content(url):
    try:
        # Check if URL is valid
        if not url or not url.startswith('http'):
            logger.error(f"Invalid URL format: {url}")
            return None

        # Set timeout and headers for request
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

@log_exception(logger)
def run_summarization(text):
    if not text or not isinstance(text, str):
        logger.error("Invalid or empty text input for summarization")
        return "Error: Invalid input text"

    # Truncate text if it's too long (OpenAI has token limits)
    max_chars = 12000  # Approximate limit for gpt-3.5-turbo
    if len(text) > max_chars:
        logger.warning(f"Text truncated from {len(text)} to {max_chars} characters")
        text = text[:max_chars]

    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes text in approximately 150 words."},
                    {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
                ],
                max_tokens=200,
                temperature=0.5
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            if "rate limit" in str(e).lower():
                if attempt < max_retries - 1:
                    logger.warning(f"Rate limit hit, retrying in {retry_delay} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("Rate limit exceeded after all retries")
                    return "Error: API rate limit exceeded"
            elif "authentication" in str(e).lower():
                logger.error("OpenAI API authentication failed - check API key configuration")
                return "Error: API authentication failed"
            else:
                logger.error(f"OpenAI API error: {str(e)}")
                return "Error: API request failed"

        except openai.error.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return "Error: API service unavailable"

        except Exception as e:
            logger.error(f"Unexpected error in summarization: {str(e)}")
            return "Error: Unable to generate summary"

@log_exception(logger)
def process_articles(session_id=None):
    try:
        # Use session_id for file naming, default to 'default' if not provided
        if not session_id:
            session_id = 'default'
        file_name = f'{session_id}_news_data.json'
        news_data_path = Config.NEWS_DATA_DIR / file_name

        if not news_data_path.exists():
            logger.error(f"News data file not found: {news_data_path}")
            return []

        with open(news_data_path, 'r') as file:
            articles = json.load(file)

        if not articles:
            logger.warning("No articles found in the data file")
            return []

        summarized_articles = []
        for article in articles:
            logger.info(f"Processing article: {article.get('title', 'Untitled')}")
            
            # Fetch full article content from URL
            content = fetch_article_content(article.get('url'))
            if content:
                summary = run_summarization(content)
            else:
                summary = run_summarization(article.get('content', ''))

            if not summary.startswith('Error:'):
                summarized_articles.append({
                    'title': article.get('title', 'Untitled'),
                    'author': article.get('author', 'Unknown Author'),
                    'source': article.get('source', {}).get('name', 'Unknown Source'),
                    'publishedAt': article.get('publishedAt'),
                    'url': article.get('url', ''),
                    'urlToImage': article.get('urlToImage'),
                    'content': article.get('content', ''),
                    'summary': summary
                })
            else:
                logger.error(f"Failed to summarize article: {article.get('title', 'Untitled')}")

        # Save summarized articles to configured path with session_id
        output_file = f'{session_id}_summarized_news.json'
        output_path = Config.SUMMARIZED_NEWS_DIR / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if summarized_articles:
            with open(output_path, 'w') as file:
                json.dump(summarized_articles, file, indent=4)
            logger.info(f"Summarized articles saved to {output_path}")
        else:
            logger.warning("No articles were successfully summarized")

        return summarized_articles

    except Exception as e:
        logger.error(f"Error processing articles: {str(e)}")
        return []

if __name__ == '__main__':
    process_articles()
