from flask import Blueprint, request, jsonify
from utils.decorators import require_auth, validate_json
from utils.errors import ValidationError, NotFoundError
from services.rating_service import RatingService
import logging

ratings_bp = Blueprint('ratings', __name__)
logger = logging.getLogger(__name__)

@ratings_bp.route('', methods=['POST'])
@require_auth
@validate_json('order_id', 'ratee_id', 'rating')
def create_rating():
    """Create rating"""
    try:
        data = request.data
        
        rating = RatingService.create_rating(
            data['order_id'],
            request.user.id,
            data['ratee_id'],
            data['rating'],
            data.get('review_text'),
            data.get('rating_type', 'courier')
        )
        
        return jsonify({
            'success': True,
            'message': 'Rating created successfully',
            'rating': rating.to_dict()
        }), 201
    except (ValidationError, NotFoundError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Create rating error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@ratings_bp.route('/user/<user_id>', methods=['GET'])
def get_user_ratings(user_id):
    """Get ratings for user"""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        ratings, total = RatingService.get_ratings(user_id, limit, offset)
        
        return jsonify({
            'success': True,
            'ratings': [r.to_dict() for r in ratings],
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset
            }
        }), 200
    except Exception as e:
        logger.error(f"Get user ratings error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
