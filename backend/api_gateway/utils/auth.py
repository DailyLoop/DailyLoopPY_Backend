#!/usr/bin/env python3
"""
Authentication Utilities

Provides the token_required decorator for protecting routes.
Validates Supabase-issued JWTs and injects user_id into Flask g.
"""

from flask import request, g, current_app
from functools import wraps
import jwt
import logging

logger = logging.getLogger(__name__)


def token_required(f):
    """Decorator to protect routes that require Supabase authentication.

    Validates the Supabase JWT in the Authorization header using the
    SUPABASE_JWT_SECRET. Sets g.user_id to the 'sub' claim (Supabase UUID)
    for use by the decorated route handler.

    Args:
        f: The route handler function to decorate.

    Returns:
        The decorated function with token validation.

    Raises:
        401: If the Authorization header is missing, malformed, or the token
             is invalid/expired.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("Missing or malformed Authorization header")
            return {'error': 'Authorization header missing or malformed'}, 401

        token = auth_header.split(' ', 1)[1]

        try:
            jwt_secret = current_app.config['SUPABASE_JWT_SECRET']
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=['HS256'],
                audience='authenticated'
            )
            g.user_id = payload['sub']
            logger.debug(f"Authenticated user: {g.user_id}")
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return {'error': 'Token has expired'}, 401
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return {'error': 'Invalid token', 'message': str(e)}, 401

        return f(*args, **kwargs)
    return decorated
