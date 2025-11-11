from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import get_config
import logging
from utils.logger import setup_logger
from utils.errors import APIError

# Initialize extensions
db = SQLAlchemy()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)

def create_app(config=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    
    # Setup CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    })
    
    # Setup logging
    setup_logger(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register shell commands
    register_shell_commands(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

def register_blueprints(app):
    """Register all route blueprints"""
    from routes import auth_bp, users_bp, orders_bp, deliveries_bp, payments_bp, ratings_bp, admin_bp, support_bp, health_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(orders_bp, url_prefix='/api/v1/orders')
    app.register_blueprint(deliveries_bp, url_prefix='/api/v1/deliveries')
    app.register_blueprint(payments_bp, url_prefix='/api/v1/payments')
    app.register_blueprint(ratings_bp, url_prefix='/api/v1/ratings')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(support_bp, url_prefix='/api/v1/support')

def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = {
            'success': False,
            'error': error.message,
            'code': error.code
        }
        return jsonify(response), error.status_code
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'success': False, 'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'success': False, 'error': 'Forbidden'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logging.error(f"Internal server error: {error}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

def register_shell_commands(app):
    """Register CLI commands"""
    @app.shell_command()
    def init_db():
        """Initialize database"""
        db.create_all()
        print("Database initialized")
    
    @app.shell_command()
    def seed_db():
        """Seed database with test data"""
        from models.user import User, UserRole
        from models.order import OrderStatus
        
        # Create admin user
        admin = User(
            email='admin@courier.com',
            first_name='Admin',
            last_name='User',
            phone='1234567890',
            role=UserRole.ADMIN
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        print("Database seeded with test data")
