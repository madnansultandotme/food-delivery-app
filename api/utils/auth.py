import jwt
import os
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
from api.models import User, UserRole

def generate_tokens(user_id, role):
    """Generate JWT access and refresh tokens"""
    secret = os.getenv('SUPABASE_JWT_SECRET', 'dev-secret-key')
    
    access_payload = {
        'user_id': user_id,
        'role': role,
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    
    refresh_payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=30),
        'iat': datetime.utcnow()
    }
    
    access_token = jwt.encode(access_payload, secret, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, secret, algorithm='HS256')
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': 86400  # 24 hours in seconds
    }

def verify_token(token):
    """Verify and decode JWT token"""
    secret = os.getenv('SUPABASE_JWT_SECRET', 'dev-secret-key')
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from headers
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user_id = payload.get('user_id')
        request.user_role = payload.get('role')
        
        return f(*args, **kwargs)
    
    return decorated_function

def role_required(*allowed_roles):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'user_role'):
                return jsonify({'error': 'User role not found'}), 401
            
            if request.user_role not in [role.value for role in allowed_roles]:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator
