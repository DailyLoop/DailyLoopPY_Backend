#!/usr/bin/env python3
"""
News API Routes

This module contains the API routes for news operations including fetching and processing.
"""

# Standard library imports
from flask import jsonify, request, make_response, g
from flask_restx import Resource, Namespace
import traceback

# Import microservices and utilities
from backend.microservices.news_fetcher import fetch_news
from backend.microservices.news_storage import store_article_in_supabase, log_user_search
from backend.microservices.summarization_service import process_articles
from backend.core.utils import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Create news namespace
news_ns = Namespace('api/news', description='News operations')

# Import token_required decorator from utils
from backend.api_gateway.utils.auth import token_required

@news_ns.route('/fetch')
class NewsFetch(Resource):
    @token_required
    @news_ns.param('keyword', 'Search keyword for news')
    @news_ns.param('session_id', 'Session ID for tracking requests')
    def get(self):
        """Fetch news articles based on a keyword and store them in Supabase.

        Requires a valid JWT token in the Authorization header.
        Fetches news articles matching the provided keyword,
        stores them in Supabase, and logs the search history for the authenticated user.

        Args:
            keyword (str): The search term for fetching news articles.
            session_id (str): Session ID for tracking the request.

        Returns:
            dict: Contains the stored article IDs and success status.
            int: HTTP 200 on success, 500 on error.
        """
        try:
            keyword = request.args.get('keyword', '')
            user_id = g.user_id
            session_id = request.args.get('session_id')
            logger.info(f"News fetch endpoint called with keyword: '{keyword}', user_id: {user_id}, session_id: {session_id}")

            logger.info(f"Fetching news articles for keyword: '{keyword}'")
            articles = fetch_news(keyword)  # This returns a list of articles.
            logger.info(f"Found {len(articles) if articles else 0} articles for keyword: '{keyword}'")

            stored_article_ids = []

            for article in articles:
                logger.debug(f"Storing article: {article.get('title', 'No title')}")
                article_id = store_article_in_supabase(article)
                stored_article_ids.append(article_id)
                logger.debug(f"Stored article with ID: {article_id}")

                if user_id:
                    logger.debug(f"Logging search for user {user_id}, article {article_id}")
                    log_user_search(user_id, article_id, session_id)

            logger.info(f"Returning {len(stored_article_ids)} article IDs")
            return make_response(jsonify({
                'status': 'success',
                'data': stored_article_ids
            }), 200)

        except Exception as e:
            # Capture the full stack trace
            stack_trace = traceback.format_exc()
            logger.error(f"Error fetching news: {str(e)}\nStack trace: {stack_trace}")
            return make_response(jsonify({
                'status': 'error',
                'message': str(e)
            }), 500)

@news_ns.route('/process')
class NewsProcess(Resource):
    @token_required
    @news_ns.param('session_id', 'Session ID for tracking requests (optional)')
    def post(self):
        """Process and summarize a batch of articles.

        Requires a valid JWT token in the Authorization header.
        Processes articles based on the provided article IDs in the request body,
        generating summaries and checking bookmark status for the authenticated user.

        Returns:
            dict: Contains processed articles data and success status.
            int: HTTP 200 on success, 401 if not authenticated, 500 on error.
        """
        try:
            session_id = request.args.get('session_id')
            user_id = g.user_id

            logger.info(f"News process endpoint called with session_id: {session_id}, user_id: {user_id}")
            
            # Get article_ids from request body
            request_data = request.get_json()
            article_ids = request_data.get('article_ids', [])
            
            logger.debug(f"Article IDs from request: {article_ids}")
            
            if not article_ids:
                return {
                    'status': 'error',
                    'message': 'No article IDs provided in request body'
                }, 400
                
            logger.info("Processing articles...")
            summarized_articles = process_articles(article_ids, user_id)
            logger.info(f"Processed {len(summarized_articles) if summarized_articles else 0} articles")
            
            return {
                'status': 'success',
                'message': 'Articles processed and summarized successfully',
                'data': summarized_articles,
                'session_id': session_id
            }, 200
            
        except Exception as e:
            # Capture the full stack trace
            stack_trace = traceback.format_exc()
            logger.error(f"Error processing articles: {str(e)}\nStack trace: {stack_trace}")
            return {
                'status': 'error',
                'message': str(e)
            }, 500