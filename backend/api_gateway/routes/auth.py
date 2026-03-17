#!/usr/bin/env python3
"""
Authentication API Routes

Supabase Auth integration for signup and login.
Tokens returned are real Supabase JWTs verifiable via SUPABASE_JWT_SECRET.
"""

from flask import request
from flask_restx import Resource, Namespace, fields
from gotrue.errors import AuthApiError

from backend.core.supabase_client import supabase
from backend.core.utils import setup_logger

logger = setup_logger(__name__)

auth_ns = Namespace('api/auth', description='Authentication operations')

signup_model = auth_ns.model('Signup', {
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password'),
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password'),
})


@auth_ns.route('/signup')
class Signup(Resource):
    @auth_ns.expect(signup_model)
    def post(self):
        """Register a new user via Supabase Auth.

        Returns the Supabase access_token (real JWT) on success.
        Supabase also creates an entry in auth.users automatically.
        """
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            logger.warning("Signup validation failed: missing email or password")
            return {'error': 'Email and password are required'}, 400

        try:
            logger.info(f"Signup request for email: {email}")
            response = supabase.auth.sign_up({'email': email, 'password': password})

            if response.user is None:
                # Supabase returns no error but no user when email confirmation
                # is required and not yet confirmed
                logger.info(f"Signup successful but email confirmation required for {email}")
                return {
                    'message': 'Signup successful. Check your email for a confirmation link.'
                }, 201

            logger.info(f"Signup successful for user: {response.user.id}")
            return {
                'message': 'User registered successfully',
                'user': {
                    'id': response.user.id,
                    'email': response.user.email,
                },
                'token': response.session.access_token if response.session else None
            }, 201

        except AuthApiError as e:
            logger.warning(f"Signup failed: {e.message}")
            return {'error': e.message}, 400
        except Exception as e:
            logger.error(f"Unexpected error during signup: {e}")
            return {'error': 'Internal server error'}, 500


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        """Authenticate user via Supabase Auth.

        Returns the Supabase access_token (real Supabase JWT) on success.
        """
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            logger.warning("Login validation failed: missing email or password")
            return {'error': 'Email and password are required'}, 400

        try:
            logger.info(f"Login attempt for email: {email}")
            response = supabase.auth.sign_in_with_password(
                {'email': email, 'password': password}
            )
            logger.info(f"Login successful for user: {response.user.id}")
            return {
                'token': response.session.access_token,
                'user': {
                    'id': response.user.id,
                    'email': response.user.email,
                }
            }, 200

        except AuthApiError as e:
            logger.warning(f"Login failed: {e.message}")
            return {'error': 'Invalid credentials'}, 401
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            return {'error': 'Internal server error'}, 500
