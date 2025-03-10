#!/usr/bin/env python3
"""
Authentication Utilities

This module provides authentication utilities for the News Aggregator API Gateway,
including the token_required decorator for protecting routes that require authentication.
"""

# Standard library imports
from flask import request
from functools import wraps
import jwt

# Import Flask app for accessing config
from flask import current_app

def token_required(f):
    """Decorator to protect routes that require authentication.
    
    This decorator validates the JWT token in the Authorization header.
    It ensures that only authenticated users can access protected endpoints.
    
    Args:
        f: The function to be decorated.
        
    Returns:
        decorated: The decorated function that includes token validation.
        
    Raises:
        401: If the token is missing or invalid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        print("[DEBUG] [api_gateway] [token_required] Checking token in request")
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            print("[DEBUG] [api_gateway] [token_required] Authorization header missing")
            return {'error': 'Authorization header missing'}, 401
        try:
            token = auth_header.split()[1]  # Extract token from 'Bearer <token>'
            print(f"[DEBUG] [api_gateway] [token_required] Decoding token: {token[:10]}...")
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], audience='authenticated')
            print(f"[DEBUG] [api_gateway] [token_required] Token decoded successfully, user: {payload.get('sub', 'unknown')}")

            return f(*args, **kwargs)
        except Exception as e:
            print(f"[DEBUG] [api_gateway] [token_required] Token validation error: {str(e)}")
            return {'error': 'Invalid token', 'message': str(e)}, 401
    return decorated