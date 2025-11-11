from database import BaseModel, db
from datetime import datetime
from enum import Enum
import bcrypt

class UserRole(Enum):
    """User roles"""
    CUSTOMER = 'customer'
    COURIER = 'courier'
    ADMIN = 'admin'

class User(BaseModel):
    """User model"""
    __tablename__ = 'users'
    
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, index=True)
    address = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, default=UserRole.CUSTOMER.value)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), nullable=True)
    verification_sent_at = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True, foreign_keys='Order.customer_id')
    assigned_deliveries = db.relationship('Delivery', backref='courier', lazy=True, foreign_keys='Delivery.courier_id')
    given_ratings = db.relationship('Rating', backref='rater', lazy=True, foreign_keys='Rating.rater_id')
    received_ratings = db.relationship('Rating', backref='ratee', lazy=True, foreign_keys='Rating.ratee_id')
    payments = db.relationship('Payment', backref='user', lazy=True)
    support_tickets = db.relationship('SupportTicket', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'profile_picture': self.profile_picture,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
        }
        if include_sensitive:
            data['email'] = self.email
        return data
