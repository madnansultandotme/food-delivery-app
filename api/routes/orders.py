from flask import Blueprint, request, jsonify
from utils.decorators import require_auth, validate_json, require_role
from utils.errors import ValidationError, NotFoundError
from services.order_service import OrderService
from models.user import UserRole
import logging

orders_bp = Blueprint('orders', __name__)
logger = logging.getLogger(__name__)

@orders_bp.route('', methods=['POST'])
@require_auth
@validate_json('pickup_address', 'delivery_address', 'package_details', 'pricing')
def create_order():
    """Create new order"""
    try:
        data = request.data
        
        order = OrderService.create_order(
            customer_id=request.user.id,
            pickup_address=data['pickup_address'],
            delivery_address=data['delivery_address'],
            package_details=data['package_details'],
            pricing=data['pricing'],
            payment_method=data.get('payment_method', 'card')
        )
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
    except (ValidationError, Exception) as e:
        logger.error(f"Create order error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@orders_bp.route('/<order_id>', methods=['GET'])
@require_auth
def get_order(order_id):
    """Get order details"""
    try:
        order = OrderService.get_order(order_id)
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        }), 200
    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Get order error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@orders_bp.route('/my-orders', methods=['GET'])
@require_auth
def get_my_orders():
    """Get customer's orders"""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        orders, total = OrderService.get_customer_orders(request.user.id, limit, offset)
        
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
        logger.error(f"Get my orders error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@orders_bp.route('/<order_id>/cancel', methods=['POST'])
@require_auth
@validate_json('reason')
def cancel_order(order_id):
    """Cancel order"""
    try:
        data = request.data
        
        order = OrderService.cancel_order(order_id, data['reason'])
        
        return jsonify({
            'success': True,
            'message': 'Order cancelled successfully',
            'order': order.to_dict()
        }), 200
    except (ValidationError, NotFoundError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Cancel order error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@orders_bp.route('/<order_id>/status', methods=['PUT'])
@require_auth
@require_role(UserRole.ADMIN.value, UserRole.COURIER.value)
@validate_json('status')
def update_order_status(order_id):
    """Update order status"""
    try:
        data = request.data
        
        order = OrderService.update_order_status(
            order_id,
            data['status'],
            request.user.id,
            data.get('reason')
        )
        
        return jsonify({
            'success': True,
            'message': 'Order status updated',
            'order': order.to_dict()
        }), 200
    except (ValidationError, NotFoundError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Update order status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
