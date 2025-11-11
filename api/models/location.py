from api.database import db, BaseModel

class DeliveryLocation(BaseModel):
    """Track delivery location history"""
    __tablename__ = 'delivery_locations'
    
    delivery_id = db.Column(db.String(36), db.ForeignKey('deliveries.id'), nullable=False)
    
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float)
    
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
