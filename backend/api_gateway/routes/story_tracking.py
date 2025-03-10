#!/usr/bin/env python3
"""
Story Tracking API Routes

This module contains the API routes for story tracking operations including
creating, retrieving, updating, and deleting tracked stories.
"""

# Standard library imports
from flask import jsonify, request, make_response
from flask_restx import Resource, Namespace
import jwt
from datetime import datetime
import os

# Import microservices and utilities
from backend.microservices.news_fetcher import fetch_news
from backend.microservices.news_storage import store_article_in_supabase
from backend.microservices.story_tracking_service import (
    get_tracked_stories, 
    create_tracked_story, 
    get_story_details, 
    delete_tracked_story, 
    toggle_polling
)
from backend.core.utils import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Create story tracking namespace
story_tracking_ns = Namespace('api/story_tracking', description='Story tracking operations')

# Import token_required decorator from utils
from backend.api_gateway.utils.auth import token_required

@story_tracking_ns.route('')
class StoryTracking(Resource):
    @story_tracking_ns.param('keyword', 'Keyword to track for news updates')
    def get(self):
        """Fetch latest news for a tracked keyword.

        Retrieves and processes the latest news articles for a given keyword.

        Args:
            keyword (str): The keyword to search for news articles.

        Returns:
            dict: Contains list of processed articles and success status.
            int: HTTP 200 on success, 400 if keyword is missing, 500 on error.
        """
        try:
            logger.debug("Story tracking get endpoint called")
            keyword = request.args.get('keyword')
            logger.debug(f"Requested keyword: '{keyword}'")
            if not keyword:
                logger.warning("Keyword parameter missing")
                return make_response(jsonify({
                    'status': 'error',
                    'message': 'Keyword parameter is required'
                }), 400)

            logger.info(f"Fetching news for keyword: '{keyword}'")
            articles = fetch_news(keyword)
            logger.info(f"Found {len(articles) if articles else 0} articles for keyword: '{keyword}'")
            
            
            processed_articles = []
            for article in articles:
                logger.debug(f"Processing article: {article.get('title', 'No title')}")
                article_id = store_article_in_supabase(article)
                logger.debug(f"Stored article with ID: {article_id}")
                processed_articles.append({
                    'id': article_id,
                    'title': article.get('title'),
                    'url': article.get('url'),
                    'source': article.get('source', {}).get('name') if isinstance(article.get('source'), dict) else article.get('source'),
                    'publishedAt': article.get('publishedAt', datetime.now().isoformat())
                })

            logger.info(f"Returning {len(processed_articles)} processed articles")
            return make_response(jsonify({
                'status': 'success',
                'articles': processed_articles
            }), 200)

        except Exception as e:
            logger.error(f"Error in story tracking: {str(e)}")
            return make_response(jsonify({
                'status': 'error',
                'message': str(e)
            }), 500)
    
    @token_required
    def post(self):
        """Create a new tracked story.

        Requires a valid JWT token in the Authorization header.
        Creates a new tracked story for the authenticated user based on a keyword and source article.

        Expected JSON payload:
        {
            'keyword': str (required),
            'sourceArticleId': str (optional)
        }

        Returns:
            dict: Contains created story details and success status.
            int: HTTP 201 on success, 400 on validation error, 500 on server error.
        """
        try:
            logger.debug("Story tracking post endpoint called")
            auth_header = request.headers.get('Authorization')
            token = auth_header.split()[1]
            logger.debug(f"Decoding token: {token[:10]}...")
            # Import app from main module to access config
            from flask import current_app
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], audience='authenticated')
            user_id = payload.get('sub')
            logger.info(f"Creating tracked story for user: {user_id}")
            
            data = request.get_json()
            keyword = data.get('keyword')
            source_article_id = data.get('sourceArticleId')
            logger.debug(f"Story details - Keyword: '{keyword}', Source article: {source_article_id}")
            
            if not keyword:
                logger.warning("Keyword parameter missing in request")
                return make_response(jsonify({
                    'status': 'error',
                    'message': 'Keyword is required'
                }), 400)
            
            logger.debug(f"Calling create_tracked_story with user_id: {user_id}, keyword: '{keyword}'")
            tracked_story = create_tracked_story(user_id, keyword, source_article_id)
            logger.info(f"Tracked story created with ID: {tracked_story['id'] if tracked_story else 'unknown'}")
            
            logger.debug(f"Getting full story details for story: {tracked_story['id']}")
            story_with_articles = get_story_details(tracked_story['id'])
            logger.info(f"Found {len(story_with_articles.get('articles', [])) if story_with_articles else 0} related articles")
            
            return make_response(jsonify({
                'status': 'success',
                'data': story_with_articles
            }), 201)
            
        except Exception as e:
            logger.error(f"Error creating tracked story: {str(e)}")
            return make_response(jsonify({
                'status': 'error',
                'message': str(e)
            }), 500)

@story_tracking_ns.route('', methods=['OPTIONS'])
class StoryTrackingOptions(Resource):
    def options(self):
        """Handle OPTIONS requests for the story tracking endpoint.

        This function sets the necessary CORS headers for preflight requests
        to the story tracking endpoint.

        Returns:
            Response: A Flask response object with appropriate CORS headers.
        """
        print("[DEBUG] [api_gateway] [story_tracking_options] Called")
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        print("[DEBUG] [api_gateway] [story_tracking_options] Responding with CORS headers")
        return response

@story_tracking_ns.route('/start')
class StartStoryTracking(Resource):
    @token_required
    def post(self):
        """Start polling for a tracked story.
        Requires a valid JWT token in the Authorization header.
        Enables polling for a specific tracked story.
        Expected JSON payload:
        {
            'story_id': str (required)
        }
        Returns:
            dict: Contains updated story details and success status.
            int: HTTP 200 on success, 400 on validation error, 404 if story not found, 500 on server error.
        """
        try:
            logger.debug("Start story tracking endpoint called")
            auth_header = request.headers.get('Authorization')
            token = auth_header.split()[1]
            logger.debug(f"Decoding token: {token[:10]}...")
            # Import app from main module to access config
            from flask import current_app
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], audience='authenticated')
            user_id = payload.get('sub')
            logger.info(f"Starting polling for user: {user_id}")
            
            data = request.get_json()
            story_id = data.get('story_id')
            logger.debug(f"Story ID: {story_id}")
            
            if not story_id:
                logger.warning("Story ID missing in request")
                return make_response(jsonify({
                    'status': 'error',
                    'message': 'Story ID is required'
                }), 400)
            
            logger.debug(f"Calling toggle_polling with user_id: {user_id}, story_id: {story_id}, enable=True")
            updated_story = toggle_polling(user_id, story_id, enable=True)
            
            if not updated_story:
                logger.warning(f"No story found with ID {story_id} for user {user_id}")
                return make_response(jsonify({
                    'status': 'error',
                    'message': 'Story not found or unauthorized'
                }), 404)
            
            logger.info(f"Polling started for story: {story_id}")
            return make_response(jsonify({
                'status': 'success',
                'message': 'Polling started successfully',
                'data': updated_story
            }), 200)
            
        except Exception as e:
            logger.error(f"Error starting polling: {str(e)}")
            return make_response(jsonify({
                'status': 'error',
                'message': str(e)
            }), 500)

@story_tracking_ns.route('/stop')
class StopStoryTracking(Resource):
    @token_required
    def post(self):
        """Stop polling for a tracked story.
        Requires a valid JWT token in the Authorization header.
        Disables polling for a specific tracked story.
        Expected JSON payload:
        {
            'story_id': str (required)
        }
        Returns:
            dict: Contains updated story details and success status.
            int: HTTP 200 on success, 400 on validation error, 404 if story not found, 500 on server error.
        """
        try:
            logger.debug("Stop story tracking endpoint called")
            auth_header = request.headers.get('Authorization')
            token = auth_header.split()[1]
            logger.debug(f"Decoding token: {token[:10]}...")
            # Import app from main module to access config
            from flask import current_app
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], audience='authenticated')
            user_id = payload.get('sub')
            logger.info(f"Stopping polling for user: {user_id}")
            
            data = request.get_json()
            story_id = data.get('story_id')
            logger.debug(f"Story ID: {story_id}")
            
            if not story_id:
                logger.warning("Story ID missing in request")
                return make_response(jsonify({
                    'status': 'error',
                    'message': 'Story ID is required'
                }), 400)
            
            logger.debug(f"Calling toggle_polling with user_id: {user_id}, story_id: {story_id}, enable=False")
            updated_story = toggle_polling(user_id, story_id, enable=False)
            
            if not updated_story:
                logger.warning(f"No story found with ID {story_id} for user {user_id}")
                return make_response(jsonify({
                    'status': 'error',
                    'message': 'Story not found or unauthorized'
                }), 404)
            
            logger.info(f"Polling stopped for story: {story_id}")
            return make_response(jsonify({
                'status': 'success',
                'message': 'Polling stopped successfully',
                'data': updated_story
            }), 200)
            
        except Exception as e:
            logger.error(f"Error stopping polling: {str(e)}")
            return make_response(jsonify({
                'status': 'error',
                'message': str(e)
            }), 500)

@story_tracking_ns.route('/user')
class UserStoryTracking(Resource):
    @token_required
    def get(self):
        """Get all tracked stories for the authenticated user.

        Requires a valid JWT token in the Authorization header.
        Retrieves all tracked stories associated with the authenticated user.

        Returns:
            dict: Contains list of tracked stories and success status.
            int: HTTP 200 on success, 500 on error.
        """
        try:
            logger.debug("User story tracking endpoint called")
            auth_header = request.headers.get('Authorization')
            token = auth_header.split()[1]
            logger.debug(f"Decoding token: {token[:10]}...")
            # Import app from main module to access config
            from flask import current_app
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], audience='authenticated')
            user_id = payload.get('sub')
            logger.info(f"Getting tracked stories for user: {user_id}")
            
            logger.debug(f"Calling get_tracked_stories")
            tracked_stories = get_tracked_stories(user_id)
            logger.info(f"Found {len(tracked_stories)} tracked stories")
            
            return make_response(jsonify({
                'status': 'success',
                'data': tracked_stories
            }), 200)
            
        except Exception as e:
            logger.error(f"Error getting tracked stories: {str(e)}")
            return make_response(jsonify({
                'status': 'error',
                'message': str(e)
            }), 500)

@story_tracking_ns.route('/<string:story_id>')
class StoryTrackingDetail(Resource):
    @token_required
    def get(self, story_id):
        """Get details for a specific tracked story.

        Requires a valid JWT token in the Authorization header.
        Retrieves detailed information about a specific tracked story.

        Args:
            story_id (str): The ID of the tracked story to retrieve.

        Returns:
            dict: Contains story details and success status.
            int: HTTP 200 on success, 404 if story not found, 500 on error.
        """
        try:
            logger.debug(f"Story tracking detail endpoint called for story: {story_id}")
            logger.debug(f"Calling get_story_details for story: {story_id}")
            story = get_story_details(story_id)
            
            if not story:
                logger.warning(f"No story found with ID: {story_id}")
                return make_response(jsonify({
                    'status': 'error',
                    'message': 'Tracked story not found'
                }), 404)
            
            logger.info(f"Found story: {story['keyword']}")
            logger.debug(f"Story has {len(story.get('articles', []))} articles")
            return make_response(jsonify({
                'status': 'success',
                'data': story
            }), 200)
            
        except Exception as e:
            logger.error(f"Error getting story details: {str(e)}")
            return make_response(jsonify({
                'status': 'error',
                'message': str(e)
            }), 500)
    
    @token_required
    def delete(self, story_id):
        """Stop tracking a story.

        Requires a valid JWT token in the Authorization header.
        Deletes a tracked story for the authenticated user.

        Args:
            story_id (str): The ID of the tracked story to delete.

        Returns:
            dict: Contains success message.
            int: HTTP 200 on success, 404 if story not found, 500 on error.
        """
        try:
            logger.debug(f"Delete story tracking endpoint called for story: {story_id}")
            auth_header = request.headers.get('Authorization')
            token = auth_header.split()[1]
            logger.debug(f"Decoding token: {token[:10]}...")
            # Import app from main module to access config
            from flask import current_app
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], audience='authenticated')
            user_id = payload.get('sub')
            logger.info(f"Deleting tracked story {story_id} for user {user_id}")
            
            logger.debug(f"Calling delete_tracked_story")
            success = delete_tracked_story(user_id, story_id)
            logger.debug(f"Delete result: {success}")
            
            if not success:
                logger.warning(f"Failed to delete story or story not found")
                return make_response(jsonify({
                    'status': 'error',
                    'message': 'Failed to delete tracked story or story not found'
                }), 404)
            
            logger.info(f"Story deleted successfully")
            return make_response(jsonify({
                'status': 'success',
                'message': 'Tracked story deleted successfully'
            }), 200)
            
        except Exception as e:
            logger.error(f"Error deleting tracked story: {str(e)}")
            return make_response(jsonify({
                'status': 'error',
                'message': str(e)
            }), 500)


