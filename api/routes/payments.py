from flask import Blueprint, request, jsonify
from utils.decorators import require_auth, validate_json, require_role
from utils.errors import ValidationError, NotFoundError
from services.payment_service import PaymentService
from models.user import UserRole
import logging

payments_bp = Blueprint('payments', __name__)
logger = logging.getLogger(__name__)

@payments_bp.route('/orders/<order_id>', methods=['POST'])
@require_auth
@validate_json('amount', 'payment_method')
def create_payment(order_id):
    """Create payment"""
    try:
        data = request.data
        
        payment = PaymentService.create_payment(
            order_id,
            request.user.id,
            data['amount'],
            data['payment_method']
        )
        
        return jsonify({
            'success': True,
            'message': 'Payment created',
            'payment': payment.to_dict()
        }), 201
    except (ValidationError, NotFoundError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Create payment error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@payments_bp.route('/<payment_id>/process', methods=['POST'])
@require_auth
@validate_json('transaction_id')
def process_payment(payment_id):
    """Process payment"""
    try:
        data = request.data
        
        payment = PaymentService.process_payment(
            payment_id,
            data['transaction_id'],
            data.get('gateway', 'stripe')
        )
        
        return jsonify({
            'success': True,
            'message': 'Payment processed successfully',
            'payment': payment.to_dict()
        }), 200
    except (ValidationError, NotFoundError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Process payment error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@payments_bp.route('/<payment_id>/refund', methods=['POST'])
@require_auth
@validate_json('reason')
def refund_payment(payment_id):
    """Refund payment"""
    try:
        data = request.data
        
        payment = PaymentService.refund_payment(payment_id, data['reason'])
        
        return jsonify({
            'success': True,
            'message': 'Payment refunded successfully',
            'payment': payment.to_dict()
        }), 200
    except (ValidationError, NotFoundError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Refund payment error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@payments_bp.route('/wallet/<user_id>/balance', methods=['GET'])
@require_auth
def get_wallet_balance(user_id):
    """Get wallet balance"""
    try:
        wallet = PaymentService.get_or_create_wallet(user_id)
        
        return jsonify({
            'success': True,
            'wallet': {
                'id': wallet.id,
                'user_id': wallet.user_id,
                'balance': wallet.balance,
                'total_added': wallet.total_added,
                'total_spent': wallet.total_spent
            }
        }), 200
    except Exception as e:
        logger.error(f"Get wallet balance error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@payments_bp.route('/wallet/<user_id>/add', methods=['POST'])
@require_auth
@validate_json('amount', 'description')
def add_wallet_balance(user_id):
    """Add balance to wallet"""
    try:
        data = request.data
        
        wallet, transaction = PaymentService.add_wallet_balance(
            user_id,
            data['amount'],
            data['description']
        )
        
        return jsonify({
            'success': True,
            'message': 'Balance added successfully',
            'wallet': {
                'balance': wallet.balance,
                'total_added': wallet.total_added
            }
        }), 200
    except (ValidationError, Exception) as e:
        logger.error(f"Add wallet balance error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
