from database import BaseModel, db
from enum import Enum
from datetime import datetime

class OrderStatus(Enum):
    """Order statuses"""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    ASSIGNED = 'assigned'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    FAILED = 'failed'

class PaymentMethod(Enum):
    """Payment methods"""
    CARD = 'card'
    WALLET = 'wallet'
    CASH_ON_DELIVERY = 'cash_on_delivery'

class Order(BaseModel):
    """Order model"""
    __tablename__ = 'orders'
    
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Pickup details
    pickup_address = db.Column(db.Text, nullable=False)
    pickup_latitude = db.Column(db.Float, nullable=False)
    pickup_longitude = db.Column(db.Float, nullable=False)
    pickup_contact = db.Column(db.String(100), nullable=False)
    pickup_phone = db.Column(db.String(20), nullable=False)
    
    # Delivery details
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_latitude = db.Column(db.Float, nullable=False)
    delivery_longitude = db.Column(db.Float, nullable=False)
    delivery_contact = db.Column(db.String(100), nullable=False)
    delivery_phone = db.Column(db.String(20), nullable=False)
    
    # Package details
    package_description = db.Column(db.Text, nullable=False)
    package_weight = db.Column(db.Float, nullable=False)
    package_dimensions = db.Column(db.String(100), nullable=True)
    special_instructions = db.Column(db.Text, nullable=True)
    
    # Pricing
    base_fare = db.Column(db.Float, nullable=False)
    distance_fare = db.Column(db.Float, default=0)
    surcharge = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default=OrderStatus.PENDING.value)
    payment_method = db.Column(db.String(30), nullable=False, default=PaymentMethod.CARD.value)
    
    # Timeline
    pickup_time = db.Column(db.DateTime, nullable=True)
    delivery_time = db.Column(db.DateTime, nullable=True)
    estimated_delivery_time = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancellation_reason = db.Column(db.Text, nullable=True)
    
    # Relationships
    delivery = db.relationship('Delivery', backref='order', uselist=False, cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False, cascade='all, delete-orphan')
    status_history = db.relationship('OrderStatusHistory', backref='order', lazy=True, cascade='all, delete-orphan')
    rating = db.relationship('Rating', backref='order', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'pickup_address': self.pickup_address,
            'delivery_address': self.delivery_address,
            'package_description': self.package_description,
            'package_weight': self.package_weight,
            'status': self.status,
            'total_amount': self.total_amount,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

class OrderStatusHistory(BaseModel):
    """Order status history"""
    __tablename__ = 'order_status_history'
    
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    from_status = db.Column(db.String(20), nullable=False)
    to_status = db.Column(db.String(20), nullable=False)
    changed_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    
    changed_by_user = db.relationship('User', foreign_keys=[changed_by])
