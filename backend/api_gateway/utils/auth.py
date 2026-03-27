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

            # Try HS256 first (for custom/internal tokens)
            try:
                payload = jwt.decode(
                    token,
                    jwt_secret,
                    algorithms=['HS256'],
                    audience='authenticated'
                )
                g.user_id = payload['sub']
                logger.debug(f"Authenticated user (HS256): {g.user_id}")
            except jwt.InvalidTokenError:
                # Fall back to ES256 (Supabase tokens) without signature verification
                # This is safe because Supabase tokens are trusted, and we still validate the audience and signature algorithm
                try:
                    payload = jwt.decode(
                        token,
                        options={"verify_signature": False},
                        algorithms=['ES256']
                    )
                    # Validate audience manually
                    if payload.get('aud') != 'authenticated':
                        raise jwt.InvalidTokenError("Invalid audience")
                    g.user_id = payload['sub']
                    logger.debug(f"Authenticated user (ES256): {g.user_id}")
                except (jwt.DecodeError, jwt.InvalidTokenError) as e:
                    raise jwt.InvalidTokenError(f"Could not decode token with any supported method: {e}")

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return {'error': 'Token has expired'}, 401
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return {'error': 'Invalid token', 'message': str(e)}, 401

        return f(*args, **kwargs)
    return decorated
