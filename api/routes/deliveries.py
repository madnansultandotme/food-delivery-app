from flask import Blueprint, request, jsonify
from utils.decorators import require_auth, validate_json, require_role
from utils.errors import ValidationError, NotFoundError
from services.delivery_service import DeliveryService
from models.user import UserRole
import logging

deliveries_bp = Blueprint('deliveries', __name__)
logger = logging.getLogger(__name__)

@deliveries_bp.route('/<order_id>/assign', methods=['POST'])
@require_auth
@require_role(UserRole.ADMIN.value)
@validate_json('courier_id')
def assign_delivery(order_id):
    """Assign delivery to courier"""
    try:
        data = request.data
        
        delivery = DeliveryService.assign_delivery(order_id, data['courier_id'])
        
        return jsonify({
            'success': True,
            'message': 'Delivery assigned successfully',
            'delivery': delivery.to_dict()
        }), 201
    except (ValidationError, NotFoundError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Assign delivery error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@deliveries_bp.route('/<delivery_id>/location', methods=['PUT'])
@require_auth
@require_role(UserRole.COURIER.value)
@validate_json('latitude', 'longitude')
def update_location(delivery_id):
    """Update delivery location"""
    try:
        data = request.data
        
        delivery = DeliveryService.update_delivery_location(
            delivery_id,
            data['latitude'],
            data['longitude'],
            data.get('accuracy'),
            data.get('speed'),
            data.get('heading'),
            data.get('altitude')
        )
        
        return jsonify({
            'success': True,
            'message': 'Location updated successfully',
            'delivery': delivery.to_dict()
        }), 200
    except (ValidationError, NotFoundError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Update location error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@deliveries_bp.route('/<delivery_id>/status', methods=['PUT'])
@require_auth
@require_role(UserRole.COURIER.value)
@validate_json('status')
def update_delivery_status(delivery_id):
    """Update delivery status"""
    try:
        data = request.data
        
        delivery = DeliveryService.update_delivery_status(delivery_id, data['status'])
        
        return jsonify({
            'success': True,
            'message': 'Delivery status updated',
            'delivery': delivery.to_dict()
        }), 200
    except (ValidationError, NotFoundError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Update delivery status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@deliveries_bp.route('/courier/<courier_id>/active', methods=['GET'])
@require_auth
def get_active_deliveries(courier_id):
    """Get courier's active deliveries"""
    try:
        deliveries = DeliveryService.get_courier_active_deliveries(courier_id)
        
        return jsonify({
            'success': True,
            'deliveries': [d.to_dict() for d in deliveries]
        }), 200
    except Exception as e:
        logger.error(f"Get active deliveries error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@deliveries_bp.route('/<delivery_id>/track', methods=['GET'])
def get_delivery_tracking(delivery_id):
    """Get delivery tracking information"""
    try:
        tracking = DeliveryService.get_delivery_tracking(delivery_id)
        
        return jsonify({
            'success': True,
            'delivery': tracking['delivery'].to_dict(),
            'location_history': [
                {
                    'id': h.id,
                    'latitude': h.latitude,
                    'longitude': h.longitude,
                    'accuracy': h.accuracy,
                    'speed': h.speed,
                    'timestamp': h.created_at.isoformat()
                } for h in tracking['location_history']
            ]
        }), 200
    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Get delivery tracking error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
