from api.database import db, BaseModel
from datetime import datetime

class PromoCode(BaseModel):
    """Promotional codes"""
    __tablename__ = 'promo_codes'
    
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    
    discount_type = db.Column(db.String(20))  # percentage, fixed
    discount_value = db.Column(db.Float, nullable=False)
    max_discount = db.Column(db.Float)  # for percentage discounts
    min_order_amount = db.Column(db.Float, default=0.0)
    
    max_uses = db.Column(db.Integer)
    current_uses = db.Column(db.Integer, default=0)
    max_uses_per_user = db.Column(db.Integer, default=1)
    
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_till = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    applicable_roles = db.Column(db.String(100))  # customer, courier
    
    def is_valid(self):
        """Check if promo code is valid"""
        now = datetime.utcnow()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_till and
            (self.max_uses is None or self.current_uses < self.max_uses)
        )
