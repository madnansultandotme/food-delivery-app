from flask import request, jsonify
from functools import wraps
import logging

def error_handler(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

def cors_handler(app):
    """Setup CORS"""
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

def request_logging(app):
    """Log all requests"""
    @app.before_request
    def log_request():
        app.logger.info(f"{request.method} {request.path}")
    
    @app.after_request
    def log_response(response):
        app.logger.info(f"Response: {response.status_code}")
        return response
