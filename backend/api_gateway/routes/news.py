#!/usr/bin/env python3
"""
News API Routes

This module contains the API routes for news operations including fetching and processing.
"""

# Standard library imports
from flask import jsonify, request, make_response
from flask_restx import Resource, Namespace
import jwt

# Import microservices and utilities
from backend.microservices.news_fetcher import fetch_news
from backend.microservices.news_storage import store_article_in_supabase, log_user_search
from backend.microservices.summarization_service import process_articles

# Create news namespace
news_ns = Namespace('api/news', description='News operations')

@news_ns.route('/fetch')
class NewsFetch(Resource):
    @news_ns.param('keyword', 'Search keyword for news')
    @news_ns.param('user_id', 'User ID for logging search history')
    @news_ns.param('session_id', 'Session ID for tracking requests')
    def get(self):
        """Fetch news articles based on a keyword and store them in Supabase.
        
        This endpoint fetches news articles matching the provided keyword,
        stores them in Supabase, and logs the search history if a user ID is provided.
        
        Args:
            keyword (str): The search term for fetching news articles.
            user_id (str, optional): User ID for logging search history.
            session_id (str): Session ID for tracking the request.
            
        Returns:
            dict: Contains the stored article IDs and success status.
            int: HTTP 200 on success, 500 on error.
        """
        try:
            keyword = request.args.get('keyword', '')
            user_id = request.args.get('user_id')  # optional
            session_id = request.args.get('session_id')
            print(f"[DEBUG] [api_gateway] [news_fetch] Called with keyword: '{keyword}', user_id: {user_id}, session_id: {session_id}")

            print(f"[DEBUG] [api_gateway] [news_fetch] Fetching news articles for keyword: '{keyword}'")
            articles = fetch_news(keyword)  # This returns a list of articles.
            print(f"[DEBUG] [api_gateway] [news_fetch] Found {len(articles) if articles else 0} articles")
            stored_article_ids = []

            for article in articles:
                print(f"[DEBUG] [api_gateway] [news_fetch] Storing article: {article.get('title', 'No title')}")
                article_id = store_article_in_supabase(article)
                stored_article_ids.append(article_id)
                print(f"[DEBUG] [api_gateway] [news_fetch] Stored article with ID: {article_id}")

                if user_id:
                    print(f"[DEBUG] [api_gateway] [news_fetch] Logging search for user {user_id}, article {article_id}")
                    log_user_search(user_id, article_id, session_id)

            print(f"[DEBUG] [api_gateway] [news_fetch] Returning {len(stored_article_ids)} article IDs")
            return make_response(jsonify({
                'status': 'success',
                'data': stored_article_ids
            }), 200)

        except Exception as e:
            print(f"[DEBUG] [api_gateway] [news_fetch] Error: {str(e)}")
            return make_response(jsonify({
                'status': 'error',
                'message': str(e)
            }), 500)

@news_ns.route('/process')
class NewsProcess(Resource):
    @news_ns.param('session_id', 'Session ID for tracking requests (optional)')
    def post(self):
        """Process and summarize a batch of articles.
        
        This endpoint processes articles based on the provided article IDs in the request body,
        generating summaries and checking bookmark status for the user if authenticated.
        
        Returns:
            dict: Contains processed articles data and success status.
            int: HTTP 200 on success, 500 on error.
        """
        try:
            session_id = request.args.get('session_id')
            
            # Try to get user_id from JWT token if it exists
            user_id = None
            auth_header = request.headers.get('Authorization')
            if auth_header:
                try:
                    token = auth_header.split()[1]  # Extract token from 'Bearer <token>'
                    # Note: The secret key should be imported from the main app
                    from flask import current_app
                    payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], audience='authenticated')
                    user_id = payload.get('sub')
                    print(f"[DEBUG] [api_gateway] [news_process] Extracted user_id from token: {user_id}")
                except Exception as e:
                    print(f"[DEBUG] [api_gateway] [news_process] Could not extract user_id from token: {str(e)}")
            
            print(f"[DEBUG] [api_gateway] [news_process] Called with session_id: {session_id}, user_id: {user_id}")
            
            # Get article_ids from request body
            request_data = request.get_json()
            article_ids = request_data.get('article_ids', [])
            
            print(f"[DEBUG] [api_gateway] [news_process] Article IDs from request: {article_ids}")
            
            if not article_ids:
                return {
                    'status': 'error',
                    'message': 'No article IDs provided in request body'
                }, 400
                
            print("[DEBUG] [api_gateway] [news_process] Processing articles...")
            summarized_articles = process_articles(article_ids, user_id)
            print(f"[DEBUG] [api_gateway] [news_process] Processed {len(summarized_articles) if summarized_articles else 0} articles")
            
            return {
                'status': 'success',
                'message': 'Articles processed and summarized successfully',
                'data': summarized_articles,
                'session_id': session_id
            }, 200
            
        except Exception as e:
            print(f"[DEBUG] [api_gateway] [news_process] Error: {str(e)}")
            # Logger should be imported from the main app
            from backend.core.utils import setup_logger
            logger = setup_logger(__name__)
            logger.error(f"Error processing articles: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }, 500