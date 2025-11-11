from app import db
from models.user import User, UserRole
from utils.errors import AuthenticationError, ConflictError, ValidationError
from utils.validators import validate_email, validate_password
import jwt
import os
from datetime import datetime, timedelta
from config import get_config

class AuthService:
    """Authentication service"""
    
    @staticmethod
    def register(email, password, first_name, last_name, phone, role='customer'):
        """Register new user"""
        # Validate inputs
        validate_email(email)
        validate_password(password)
        
        if len(first_name) < 2 or len(last_name) < 2:
            raise ValidationError('First and last names must be at least 2 characters')
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ConflictError(f'User with email {email} already exists')
        
        # Create user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role if role in [r.value for r in UserRole] else UserRole.CUSTOMER.value
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def login(email, password):
        """Authenticate user"""
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            raise AuthenticationError('Invalid email or password')
        
        if not user.is_active:
            raise AuthenticationError('User account is inactive')
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return user
    
    @staticmethod
    def generate_tokens(user_id):
        """Generate JWT tokens"""
        config = get_config()
        secret_key = config.JWT_SECRET_KEY
        
        access_payload = {
            'user_id': user_id,
            'type': 'access',
            'exp': datetime.utcnow() + config.JWT_ACCESS_TOKEN_EXPIRES,
            'iat': datetime.utcnow()
        }
        
        refresh_payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + config.JWT_REFRESH_TOKEN_EXPIRES,
            'iat': datetime.utcnow()
        }
        
        access_token = jwt.encode(access_payload, secret_key, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, secret_key, algorithm='HS256')
        
        return access_token, refresh_token
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token"""
        config = get_config()
        secret_key = config.JWT_SECRET_KEY
        
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            if payload.get('type') != 'access':
                raise AuthenticationError('Invalid token type')
            
            user = User.query.get(payload['user_id'])
            if not user:
                raise AuthenticationError('User not found')
            
            return user
        except jwt.ExpiredSignatureError:
            raise AuthenticationError('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationError('Invalid token')
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """Refresh access token"""
        config = get_config()
        secret_key = config.JWT_SECRET_KEY
        
        try:
            payload = jwt.decode(refresh_token, secret_key, algorithms=['HS256'])
            
            if payload.get('type') != 'refresh':
                raise AuthenticationError('Invalid token type')
            
            user_id = payload['user_id']
            access_token, _ = AuthService.generate_tokens(user_id)
            
            return access_token
        except jwt.ExpiredSignatureError:
            raise AuthenticationError('Refresh token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationError('Invalid refresh token')
