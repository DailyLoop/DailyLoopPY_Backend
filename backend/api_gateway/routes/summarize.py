#!/usr/bin/env python3
"""
Summarization API Routes

This module contains the API routes for text summarization operations.
"""

# Standard library imports
from flask import request
from flask_restx import Resource, Namespace, fields

# Import microservices and utilities
from backend.microservices.summarization_service import run_summarization
from backend.core.utils import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Create summarize namespace
summarize_ns = Namespace('summarize', description='Text summarization operations')

# Define API models for request/response documentation
article_model = summarize_ns.model('Article', {
    'article_text': fields.String(required=True, description='The text to summarize')
})

@summarize_ns.route('/')
class Summarize(Resource):
    @summarize_ns.expect(article_model)
    def post(self):
        """Summarize the provided article text.
        
        Expects a JSON payload with 'article_text' field.
        Uses the summarization service to generate a concise summary.
        
        Returns:
            dict: Contains the generated summary.
            int: HTTP 200 status code on success.
        """
        logger.info("Summarize endpoint called")
        data = request.get_json()
        article_text = data.get('article_text', '')
        logger.debug(f"Summarizing text of length: {len(article_text)}")
        summary = run_summarization(article_text)
        logger.debug(f"Summarization complete, summary length: {len(summary)}")
        return {"summary": summary}, 200