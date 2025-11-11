from flask import Blueprint, request, jsonify
from utils.decorators import require_auth, require_role, validate_json
from utils.errors import ValidationError
from services.user_service import UserService
from models.user import UserRole
import logging

users_bp = Blueprint('users', __name__)
logger = logging.getLogger(__name__)

@users_bp.route('/<user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """Get user profile"""
    try:
        user = UserService.get_user(user_id)
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@users_bp.route('/profile', methods=['PUT'])
@require_auth
@validate_json('first_name', 'last_name')
def update_profile():
    """Update user profile"""
    try:
        data = request.data
        user = UserService.update_profile(request.user.id, **data)
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    except (ValidationError, Exception) as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@users_bp.route('/location', methods=['PUT'])
@require_auth
@validate_json('latitude', 'longitude')
def update_location():
    """Update user location"""
    try:
        data = request.data
        user = UserService.update_location(request.user.id, data['latitude'], data['longitude'])
        
        return jsonify({
            'success': True,
            'message': 'Location updated successfully',
            'user': user.to_dict()
        }), 200
    except (ValidationError, Exception) as e:
        logger.error(f"Update location error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@users_bp.route('/courier/<courier_id>/stats', methods=['GET'])
def get_courier_stats(courier_id):
    """Get courier statistics"""
    try:
        stats = UserService.get_courier_stats(courier_id)
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    except Exception as e:
        logger.error(f"Get courier stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
