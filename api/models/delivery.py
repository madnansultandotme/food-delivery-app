from database import BaseModel, db
from enum import Enum

class DeliveryStatus(Enum):
    """Delivery statuses"""
    ASSIGNED = 'assigned'
    PICKED_UP = 'picked_up'
    IN_TRANSIT = 'in_transit'
    REACHED_DESTINATION = 'reached_destination'
    DELIVERED = 'delivered'
    FAILED = 'failed'

class Delivery(BaseModel):
    """Delivery model"""
    __tablename__ = 'deliveries'
    
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False, unique=True)
    courier_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Status
    status = db.Column(db.String(30), default=DeliveryStatus.ASSIGNED.value)
    
    # Current location
    current_latitude = db.Column(db.Float, nullable=True)
    current_longitude = db.Column(db.Float, nullable=True)
    
    # Timestamps
    assigned_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    pickup_at = db.Column(db.DateTime, nullable=True)
    delivery_at = db.Column(db.DateTime, nullable=True)
    estimated_arrival = db.Column(db.DateTime, nullable=True)
    
    # Additional info
    delivery_notes = db.Column(db.Text, nullable=True)
    proof_of_delivery = db.Column(db.String(255), nullable=True)
    recipient_name = db.Column(db.String(100), nullable=True)
    recipient_signature = db.Column(db.String(255), nullable=True)
    
    # Relationships
    location_history = db.relationship('DeliveryLocationHistory', backref='delivery', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'courier_id': self.courier_id,
            'status': self.status,
            'current_latitude': self.current_latitude,
            'current_longitude': self.current_longitude,
            'estimated_arrival': self.estimated_arrival.isoformat() if self.estimated_arrival else None,
            'created_at': self.created_at.isoformat(),
        }

class DeliveryLocationHistory(BaseModel):
    """Track delivery location history"""
    __tablename__ = 'delivery_location_history'
    
    delivery_id = db.Column(db.String(36), db.ForeignKey('deliveries.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    speed = db.Column(db.Float, nullable=True)
    heading = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
