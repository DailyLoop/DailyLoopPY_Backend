#!/usr/bin/env python3
"""API Gateway for the News Aggregator Backend

This module serves as the central API Gateway for the News Aggregator application.
It provides a unified interface for clients to interact with various microservices
including news fetching, summarization, authentication, and story tracking.

Key Features:
- RESTful API endpoints using Flask-RestX
- JWT-based authentication
- CORS support for cross-origin requests
- Swagger documentation
- Error handling and logging
- Integration with multiple microservices

Endpoints:
- /api/news: News fetching and processing
- /health: System health check
- /summarize: Article summarization
- /api/user: User profile management
- /api/auth: Authentication operations
- /api/bookmarks: Bookmark management
- /api/story_tracking: Story tracking functionality
"""

# Standard library imports
from flask import Blueprint, Flask, jsonify, request, make_response
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace
import sys
import os
import jwt
import json
import uuid
import datetime
from datetime import datetime, timedelta
from functools import wraps

# Add project root to Python path for relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Import microservices and utilities
from backend.microservices.summarization_service import run_summarization, process_articles
from backend.microservices.news_fetcher import fetch_news
from backend.core.config import Config
from backend.core.utils import setup_logger, log_exception
from backend.microservices.auth_service import load_users
from backend.microservices.news_storage import store_article_in_supabase, log_user_search, add_bookmark, get_user_bookmarks, delete_bookmark
from backend.microservices.story_tracking_service import get_tracked_stories, create_tracked_story, get_story_details, delete_tracked_story
from backend.api_gateway.utils.auth import token_required

# Initialize logger for the API Gateway
logger = setup_logger(__name__)
logger.info("API Gateway starting up...")

# Initialize Flask application with security configurations
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')  # JWT secret key for token signing
logger.info("Flask app initialized with security configurations")

# Configure CORS to allow specific origins and methods
allowed_origins = ["http://localhost:5173", "http://localhost:8080"]
CORS(app, 
     origins=allowed_origins, 
     supports_credentials=True, 
     allow_headers=["Content-Type", "Authorization"], 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
logger.info(f"CORS configured with allowed origins: {allowed_origins}")

# Initialize Flask-RestX for API documentation
api = Api(app, version='1.0', title='News Aggregator API',
          description='A news aggregation and summarization API')
logger.info("Flask-RestX API initialized with documentation support")

# Import namespaces from route modules
try:
    from backend.api_gateway.routes.news import news_ns
    from backend.api_gateway.routes.auth import auth_ns
    from backend.api_gateway.routes.health import health_ns
    from backend.api_gateway.routes.summarize import summarize_ns
    from backend.api_gateway.routes.user import user_ns
    from backend.api_gateway.routes.bookmark import bookmark_ns
    from backend.api_gateway.routes.story_tracking import story_tracking_ns
    
    # Register imported namespaces with the API
    api.add_namespace(news_ns)
    api.add_namespace(auth_ns)
    api.add_namespace(health_ns)
    api.add_namespace(summarize_ns)
    api.add_namespace(user_ns)
    api.add_namespace(bookmark_ns)
    api.add_namespace(story_tracking_ns)
    logger.info("All API namespaces successfully registered")
except Exception as e:
    logger.error(f"Error loading API namespaces: {str(e)}")
    raise

# token_required decorator is now in utils/auth.py

# Define API models for request/response documentation

# User profile model is now defined in routes/user.py

# API models for other endpoints are defined in their respective modules

logger.info("API Gateway initialization completed successfully")

if __name__ == '__main__':
    try:
        # Read the port from the environment (Cloud Run sets the PORT variable)
        port = int(os.environ.get("PORT", 8080))
        logger.info(f"Starting server on port {port}")
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}")
        sys.exit(1)
