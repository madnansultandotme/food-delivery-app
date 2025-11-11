from flask import Blueprint, request, jsonify
from app import limiter
from utils.decorators import validate_json, require_auth, rate_limit
from utils.errors import AuthenticationError, ValidationError
from services.auth_service import AuthService
from models.user import User, UserRole
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
@rate_limit('10 per hour')
@validate_json('email', 'password', 'first_name', 'last_name', 'phone')
def register():
    """Register new user"""
    try:
        data = request.data
        
        user = AuthService.register(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            role=data.get('role', 'customer')
        )
        
        access_token, refresh_token = AuthService.generate_tokens(user.id)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 201
    except (ValidationError, Exception) as e:
        logger.error(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@auth_bp.route('/login', methods=['POST'])
@rate_limit('20 per hour')
@validate_json('email', 'password')
def login():
    """Login user"""
    try:
        data = request.data
        
        user = AuthService.login(data['email'], data['password'])
        access_token, refresh_token = AuthService.generate_tokens(user.id)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200
    except (AuthenticationError, Exception) as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 401

@auth_bp.route('/refresh', methods=['POST'])
@validate_json('refresh_token')
def refresh():
    """Refresh access token"""
    try:
        data = request.data
        access_token = AuthService.refresh_access_token(data['refresh_token'])
        
        return jsonify({
            'success': True,
            'access_token': access_token
        }), 200
    except (AuthenticationError, Exception) as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 401

@auth_bp.route('/verify', methods=['GET'])
@require_auth
def verify_token():
    """Verify token"""
    return jsonify({
        'success': True,
        'user': request.user.to_dict()
    }), 200
