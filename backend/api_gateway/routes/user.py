#!/usr/bin/env python3
"""
User API Routes

This module contains the API routes for user operations including profile management.
"""

# Standard library imports
from flask import jsonify, request, make_response
from flask_restx import Resource, Namespace, fields
import jwt

# Import microservices and utilities
from backend.microservices.auth_service import load_users
from functools import wraps
from flask import current_app

# Create user namespace
user_ns = Namespace('api/user', description='User operations')

# Define API models for request/response documentation
user_profile_model = user_ns.model('UserProfile', {
    'id': fields.String(description='User ID'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email address'),
    'firstName': fields.String(description='First name'),
    'lastName': fields.String(description='Last name'),
    'avatarUrl': fields.String(description='URL to user avatar')
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
        Returns the user's profile data excluding sensitive information.
        
        Returns:
            dict: User profile data including id, username, email, and names.
            int: HTTP 200 on success, 404 if user not found.
        """
        print("[DEBUG] [api_gateway] [user_profile] Called")
        auth_header = request.headers.get('Authorization')
        token = auth_header.split()[1]
        print(f"[DEBUG] [api_gateway] [user_profile] Decoding token: {token[:10]}...")
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], audience='authenticated')
        print(f"[DEBUG] [api_gateway] [user_profile] Looking up user with ID: {payload.get('sub')}")
        
        users = load_users()
        user = next((u for u in users if u.get('id') == payload.get('sub')), None)
        if not user:
            print(f"[DEBUG] [api_gateway] [user_profile] User not found with ID: {payload.get('sub')}")
            return {'error': 'User not found'}, 404
            
        print(f"[DEBUG] [api_gateway] [user_profile] Found user: {user.get('username')}")
        return {k: user[k] for k in user if k != 'password'}, 200