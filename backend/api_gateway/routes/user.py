#!/usr/bin/env python3
"""
User API Routes

This module contains the API routes for user operations including profile management.
"""

# Standard library imports
from flask import jsonify, request, make_response, g
from flask_restx import Resource, Namespace, fields

# Import microservices and utilities
from backend.core.supabase_client import supabase
from backend.core.utils import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Create user namespace
user_ns = Namespace('api/user', description='User operations')

# Define API models for request/response documentation
user_profile_model = user_ns.model('UserProfile', {
    'id': fields.String(description='User ID'),
    'email': fields.String(description='Email address'),
})

# Import token_required decorator from utils
from backend.api_gateway.utils.auth import token_required

@user_ns.route('/profile')
class UserProfile(Resource):
    @token_required
    @user_ns.marshal_with(user_profile_model)
    def get(self):
        """Retrieve authenticated user's profile information.

        Requires a valid JWT token in the Authorization header.
        Returns the user's profile data from Supabase.

        Returns:
            dict: User profile data including id and email.
            int: HTTP 200 on success, 404 if user not found.
        """
        logger.info("User profile endpoint called")
        user_id = g.user_id
        logger.debug(f"Looking up user profile for ID: {user_id}")

        try:
            result = supabase.table("profiles").select("*").eq("id", user_id).execute()
            if not result.data:
                logger.warning(f"User profile not found with ID: {user_id}")
                return {'error': 'User not found'}, 404

            logger.debug(f"Found user profile")
            return result.data[0], 200
        except Exception as e:
            logger.error(f"Error retrieving user profile: {str(e)}")
            return {'error': 'Internal server error'}, 500
