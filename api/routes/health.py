from flask import Blueprint, jsonify
from app import db
import logging

health_bp = Blueprint('health', __name__)
logger = logging.getLogger(__name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        db.session.commit()
        
        return jsonify({
            'status': 'healthy',
            'service': 'Courier Delivery API',
            'version': 'v1.0.0',
            'database': 'connected'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'Courier Delivery API',
            'error': str(e)
        }), 500
