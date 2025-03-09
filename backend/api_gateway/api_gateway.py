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

print("[DEBUG] [api_gateway] [startup] API Gateway starting up...")

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
print("[DEBUG] [api_gateway] [startup] Environment variables loaded")

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
print("[DEBUG] [api_gateway] [startup] Logger initialized")

# Initialize Flask application with security configurations
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')  # JWT secret key for token signing
print("[DEBUG] [api_gateway] [startup] Flask app initialized with secret key")

# Configure CORS to allow specific origins and methods
CORS(app, 
     origins=["http://localhost:5173", "http://localhost:8080"], 
     supports_credentials=True, 
     allow_headers=["Content-Type", "Authorization"], 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
print("[DEBUG] [api_gateway] [startup] CORS configured")

# Initialize Flask-RestX for API documentation
api = Api(app, version='1.0', title='News Aggregator API',
          description='A news aggregation and summarization API')
print("[DEBUG] [api_gateway] [startup] Flask-RestX API initialized")

# Import namespaces from route modules
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
print("[DEBUG] [api_gateway] [startup] API namespaces defined and registered")

# token_required decorator is now in utils/auth.py

# Define API models for request/response documentation

# User profile model is now defined in routes/user.py

# API models for other endpoints are defined in their respective modules

print("[DEBUG] [api_gateway] [startup] API models defined")

# Health check endpoint is now in routes/health.py

# News endpoints are now in routes/news.py

# Auth endpoints are now in routes/auth.py

# User profile endpoint is now in routes/user.py

# Story tracking endpoints are now in routes/story_tracking.py

# StartStoryTracking endpoint is now in routes/story_tracking.py

# StopStoryTracking endpoint is now in routes/story_tracking.py

# UserStoryTracking endpoint is now in routes/story_tracking.py

# StoryTrackingDetail endpoint is now in routes/story_tracking.py

# story_tracking_options function is now handled by Flask-CORS

if __name__ == '__main__':
    # Read the port from the environment (Cloud Run sets the PORT variable)
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port)
