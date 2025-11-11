from functools import wraps
from flask import request, jsonify
from app import limiter
from utils.errors import AuthenticationError, ValidationError
from services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)

def require_auth(f):
    """Require authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                raise AuthenticationError('Invalid authorization header format')
        
        if not token:
            raise AuthenticationError('Missing authorization token')
        
        try:
            user = AuthService.verify_token(token)
            request.user = user
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise AuthenticationError('Invalid or expired token')
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(*roles):
    """Require specific role decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'user'):
                raise AuthenticationError('User not authenticated')
            
            if request.user.role not in [r.value if hasattr(r, 'value') else r for r in roles]:
                raise AuthenticationError('Insufficient permissions')
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json(*required_fields):
    """Validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                raise ValidationError('Request body must be JSON')
            
            data = request.get_json()
            
            for field in required_fields:
                if field not in data or data[field] is None:
                    raise ValidationError(f'Missing required field: {field}')
            
            request.data = data
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(limit='50 per hour'):
    """Rate limit decorator"""
    def decorator(f):
        @wraps(f)
        @limiter.limit(limit)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator
