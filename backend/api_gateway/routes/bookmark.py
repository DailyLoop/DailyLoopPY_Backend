#!/usr/bin/env python3
"""
Bookmark API Routes

This module contains the API routes for bookmark operations including adding, listing, and deleting bookmarks.
"""

# Standard library imports
from flask import jsonify, request, make_response
from flask_restx import Resource, Namespace
import jwt
from functools import wraps
from flask import current_app

# Import microservices and utilities
from backend.microservices.news_storage import add_bookmark, get_user_bookmarks, delete_bookmark
from backend.core.utils import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Create bookmark namespace
bookmark_ns = Namespace('api/bookmarks', description='Bookmark operations')

# Import token_required decorator from utils
from backend.api_gateway.utils.auth import token_required

@bookmark_ns.route('/')
class Bookmark(Resource):
    @token_required
    def get(self):
        """Retrieve all bookmarks for the authenticated user.
        
        Requires a valid JWT token in the Authorization header.
        Returns a list of bookmarked articles for the current user.
        
        Returns:
            dict: Contains list of bookmarked articles and success status.
            int: HTTP 200 on success, 500 on error.
        """
        try:
            print("[DEBUG] [api_gateway] [get_bookmarks] Called")
            auth_header = request.headers.get('Authorization')
            token = auth_header.split()[1]
            print(f"[DEBUG] [api_gateway] [get_bookmarks] Decoding token: {token[:10]}...")
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], audience='authenticated')
            user_id = payload.get('sub')
            print(f"[DEBUG] [api_gateway] [get_bookmarks] Getting bookmarks for user: {user_id}")

            bookmarks = get_user_bookmarks(user_id)
            print(f"[DEBUG] [api_gateway] [get_bookmarks] Found {len(bookmarks)} bookmarks")

            return {
                'status': 'success',
                'data': bookmarks
            }, 200

        except Exception as e:
            print(f"[DEBUG] [api_gateway] [get_bookmarks] Error: {str(e)}")
            logger.error(f"Error fetching bookmarks: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }, 500

    @token_required
    def post(self):
        """Add a new bookmark for the authenticated user.
        
        Requires a valid JWT token in the Authorization header.
        Creates a bookmark linking the user to a specific news article.
        
        Expected JSON payload:
        {
            'news_id': str (required)
        }
        
        Returns:
            dict: Contains bookmark ID and success status.
            int: HTTP 201 on success, 400 on validation error, 500 on server error.
        """
        try:
            print("[DEBUG] [api_gateway] [add_bookmark] Called")
            auth_header = request.headers.get('Authorization')
            token = auth_header.split()[1]
            print(f"[DEBUG] [api_gateway] [add_bookmark] Decoding token: {token[:10]}...")
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], audience='authenticated')
            user_id = payload.get('sub')
            print(f"[DEBUG] [api_gateway] [add_bookmark] Adding bookmark for user: {user_id}")

            data = request.get_json()
            news_id = data.get('news_id')
            print(f"[DEBUG] [api_gateway] [add_bookmark] News article ID: {news_id}")

            if not news_id:
                print("[DEBUG] [api_gateway] [add_bookmark] News article ID missing in request")
                return {'error': 'News article ID is required'}, 400

            print(f"[DEBUG] [api_gateway] [add_bookmark] Adding bookmark for user {user_id}, article {news_id}")
            bookmark = add_bookmark(user_id, news_id)
            print(f"[DEBUG] [api_gateway] [add_bookmark] Bookmark added with ID: {bookmark['id'] if isinstance(bookmark, dict) else bookmark}")
            
            return {
                'status': 'success',
                'message': 'Bookmark added successfully',
                'data': {
                    'bookmark_id': bookmark['id'] if isinstance(bookmark, dict) else bookmark
                }
            }, 201

        except Exception as e:
            print(f"[DEBUG] [api_gateway] [add_bookmark] Error: {str(e)}")
            logger.error(f"Error adding bookmark: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }, 500

@bookmark_ns.route('/<string:bookmark_id>')
class BookmarkDelete(Resource):
    @token_required
    def delete(self, bookmark_id):
        """Remove a bookmark for a news article.

        Requires a valid JWT token in the Authorization header.
        Deletes the specified bookmark for the authenticated user.

        Args:
            bookmark_id (str): The ID of the bookmark to be deleted.

        Returns:
            dict: Contains success message.
            int: HTTP 200 on success, 500 on error.
        """
        try:
            print(f"[DEBUG] [api_gateway] [delete_bookmark] Called for bookmark: {bookmark_id}")
            auth_header = request.headers.get('Authorization')
            token = auth_header.split()[1]
            print(f"[DEBUG] [api_gateway] [delete_bookmark] Decoding token: {token[:10]}...")
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], audience='authenticated')
            user_id = payload.get('sub')
            print(f"[DEBUG] [api_gateway] [delete_bookmark] Deleting bookmark {bookmark_id} for user {user_id}")

            result = delete_bookmark(user_id, bookmark_id)
            print(f"[DEBUG] [api_gateway] [delete_bookmark] Deletion result: {result}")
            
            return {
                'status': 'success',
                'message': 'Bookmark removed successfully'
            }, 200

        except Exception as e:
            print(f"[DEBUG] [api_gateway] [delete_bookmark] Error: {str(e)}")
            logger.error(f"Error removing bookmark: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }, 500