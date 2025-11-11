from .health import health_bp
from .auth import auth_bp
from .users import users_bp
from .orders import orders_bp
from .deliveries import deliveries_bp
from .payments import payments_bp
from .ratings import ratings_bp
from .admin import admin_bp
from .support import support_bp

__all__ = [
    'health_bp',
    'auth_bp',
    'users_bp',
    'orders_bp',
    'deliveries_bp',
    'payments_bp',
    'ratings_bp',
    'admin_bp',
    'support_bp',
]
