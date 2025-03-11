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
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
import sys
import os

# Add project root to Python path for relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Import microservices and utilities
from backend.core.utils import setup_logger

from backend.api_gateway.routes.news import news_ns
from backend.api_gateway.routes.auth import auth_ns
from backend.api_gateway.routes.health import health_ns
from backend.api_gateway.routes.summarize import summarize_ns
from backend.api_gateway.routes.user import user_ns
from backend.api_gateway.routes.bookmark import bookmark_ns
from backend.api_gateway.routes.story_tracking import story_tracking_ns

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
