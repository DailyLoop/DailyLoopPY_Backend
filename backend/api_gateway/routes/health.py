#!/usr/bin/env python3
"""
Health API Routes

This module contains the API routes for health check operations.
"""

# Standard library imports
from flask import jsonify, request
from flask_restx import Resource, Namespace

# Create health namespace
health_ns = Namespace('health', description='Health check operations')

@health_ns.route('/')
class HealthCheck(Resource):
    def get(self):
        """Check the health status of the API Gateway.
        
        Returns:
            dict: A dictionary containing the health status.
            int: HTTP 200 status code indicating success.
        """
        print("[DEBUG] [api_gateway] [health_check] Called")
        return {"status": "API Gateway is healthy"}, 200