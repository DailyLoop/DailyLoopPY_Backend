#!/usr/bin/env python3
"""
Authentication API Routes

This module contains the API routes for authentication operations including signup, login, and token management.
"""

# Standard library imports
from flask import jsonify, request, make_response
from flask_restx import Resource, Namespace, fields
import jwt
import uuid
import datetime
import os
import json
from functools import wraps

# Import microservices and utilities
from backend.microservices.auth_service import load_users
from backend.core.utils import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Create auth namespace
auth_ns = Namespace('api/auth', description='Authentication operations')

# Define API models for request/response documentation
signup_model = auth_ns.model('Signup', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
    'email': fields.String(required=True, description='Email address'),
    'firstName': fields.String(required=False, description='First name'),
    'lastName': fields.String(required=False, description='Last name')
})

@auth_ns.route('/signup')
class Signup(Resource):
    @auth_ns.expect(signup_model)
    def post(self):
        """Register a new user in the system.
        
        Creates a new user account with the provided information and generates
        a JWT token for immediate authentication.
        
        Expected JSON payload:
        {
            'username': str (required),
            'password': str (required),
            'email': str (required),
            'firstName': str (optional),
            'lastName': str (optional)
        }
        
        Returns:
            dict: Contains user data (excluding password) and JWT token.
            int: HTTP 201 on success, 400 on validation error, 500 on server error.
        """
        logger.info("User signup endpoint called")
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        firstName = data.get('firstName', '')
        lastName = data.get('lastName', '')
        logger.info(f"Signup request for username: {username}, email: {email}")

        if not username or not password or not email:
            logger.warning("Signup validation failed: missing required fields")
            return {'error': 'Username, password, and email are required'}, 400

        users = load_users()
        logger.debug(f"Loaded {len(users)} existing users")

        # Check if username already exists
        if any(u.get('username') == username for u in users):
            logger.warning(f"Signup failed: Username {username} already exists")
            return {'error': 'Username already exists'}, 400

        # Create new user with unique ID
        new_user = {
            'id': str(uuid.uuid4()),
            'username': username,
            'password': password,
            'email': email,
            'firstName': firstName,
            'lastName': lastName
        }
        logger.debug(f"Created new user with ID: {new_user['id']}")
        
        users.append(new_user)

        try:
            # Save updated users list
            logger.debug("Saving updated users list")
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'users.txt'), 'w') as f:
                json.dump(users, f, indent=4)
            logger.debug("Users list saved successfully")
        except Exception as e:
            logger.error(f"Error saving user data: {str(e)}")
            return {'error': 'Failed to save user data', 'message': str(e)}, 500

        # Generate JWT token
        logger.debug("Generating JWT token")
        from flask import current_app
        token = jwt.encode({
            'sub': new_user['id'],
            'username': new_user['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'aud': 'authenticated'
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        logger.debug(f"Token generated: {token[:10]}...")

        # Exclude password from response
        user_data = {k: new_user[k] for k in new_user if k != 'password'}
        logger.info("Signup successful")
        return {'message': 'User registered successfully', 'user': user_data, 'token': token}, 201

@auth_ns.route('/login')
class Login(Resource):
    def post(self):
        """Authenticate user and generate JWT token.
        
        Validates user credentials and generates a JWT token for authenticated access.
        
        Expected JSON payload:
        {
            'username': str (required),
            'password': str (required)
        }
        
        Returns:
            dict: Contains user data (excluding password) and JWT token.
            int: HTTP 200 on success, 400 on validation error, 401 on invalid credentials.
        """
        logger.info("Login endpoint called")
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        logger.info(f"Login attempt for username: {username}")
        
        if not username or not password:
            logger.warning("Login validation failed: missing username or password")
            return {'error': 'Username and password are required'}, 400
        
        users = load_users()
        logger.debug(f"Loaded {len(users)} users")
        user = next((u for u in users if u.get('username') == username and u.get('password') == password), None)
        
        if not user:
            logger.warning(f"Invalid credentials for username: {username}")
            return {'error': 'Invalid credentials'}, 401
        
        logger.debug(f"Valid credentials for user: {user.get('id')}")
        logger.debug("Generating JWT token")
        from flask import current_app
        token = jwt.encode({
            'sub': user['id'],
            'username': user['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'aud': 'authenticated'
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        logger.debug(f"Token generated: {token[:10]}...")
        
        user_data = {k: user[k] for k in user if k != 'password'}
        logger.info("Login successful")
        return {'token': token, 'user': user_data}