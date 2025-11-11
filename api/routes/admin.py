from flask import Blueprint, request, jsonify
from utils.decorators import require_auth, require_role, validate_json
from utils.errors import NotFoundError
from services.user_service import UserService
from models.user import UserRole, User
from models.order import Order
from models.delivery import Delivery
from app import db
from sqlalchemy import func
import logging

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

@admin_bp.route('/dashboard/stats', methods=['GET'])
@require_auth
@require_role(UserRole.ADMIN.value)
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Total users by role
        total_customers = User.query.filter_by(role=UserRole.CUSTOMER.value).count()
        total_couriers = User.query.filter_by(role=UserRole.COURIER.value).count()
        
        # Order statistics
        total_orders = Order.query.count()
        completed_orders = Order.query.filter_by(status='delivered').count()
        pending_orders = Order.query.filter_by(status='pending').count()
        
        # Revenue statistics
        total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
        
        # Active deliveries
        active_deliveries = Delivery.query.filter(
            Delivery.status.in_(['assigned', 'picked_up', 'in_transit'])
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'users': {
                    'total_customers': total_customers,
                    'total_couriers': total_couriers
                },
                'orders': {
                    'total': total_orders,
                    'completed': completed_orders,
                    'pending': pending_orders
                },
                'revenue': {
                    'total': float(total_revenue)
                },
                'active_deliveries': active_deliveries
            }
        }), 200
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@admin_bp.route('/users', methods=['GET'])
@require_auth
@require_role(UserRole.ADMIN.value)
def get_all_users():
    """Get all users"""
    try:
        role = request.args.get('role')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = User.query
        if role:
            query = query.filter_by(role=role)
        
        users = query.limit(limit).offset(offset).all()
        total = query.count()
        
        return jsonify({
            'success': True,
            'users': [u.to_dict() for u in users],
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset
            }
        }), 200
    except Exception as e:
        logger.error(f"Get all users error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@admin_bp.route('/users/<user_id>/deactivate', methods=['POST'])
@require_auth
@require_role(UserRole.ADMIN.value)
def deactivate_user(user_id):
    """Deactivate user"""
    try:
        user = UserService.deactivate_user(user_id)
        
        return jsonify({
            'success': True,
            'message': 'User deactivated successfully',
            'user': user.to_dict()
        }), 200
    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Deactivate user error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@admin_bp.route('/users/<user_id>/activate', methods=['POST'])
@require_auth
@require_role(UserRole.ADMIN.value)
def activate_user(user_id):
    """Activate user"""
    try:
        user = UserService.activate_user(user_id)
        
        return jsonify({
            'success': True,
            'message': 'User activated successfully',
            'user': user.to_dict()
        }), 200
    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Activate user error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@admin_bp.route('/orders', methods=['GET'])
@require_auth
@require_role(UserRole.ADMIN.value)
def get_all_orders():
    """Get all orders"""
    try:
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = Order.query
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc()).limit(limit).offset(offset).all()
        total = query.count()
        
        return jsonify({
            'success': True,
            'orders': [o.to_dict() for o in orders],
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset
            }
        }), 200
    except Exception as e:
        logger.error(f"Get all orders error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
