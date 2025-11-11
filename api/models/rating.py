from database import BaseModel, db

class Rating(BaseModel):
    """Rating model"""
    __tablename__ = 'ratings'
    
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    rater_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    ratee_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Rating
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    review_text = db.Column(db.Text, nullable=True)
    
    # What was being rated
    rating_type = db.Column(db.String(20), nullable=False)  # courier, customer, service
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'rater_id': self.rater_id,
            'ratee_id': self.ratee_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'rating_type': self.rating_type,
            'created_at': self.created_at.isoformat(),
        }
