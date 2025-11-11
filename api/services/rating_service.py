from app import db
from models.rating import Rating
from models.order import Order
from utils.errors import NotFoundError, ValidationError
from utils.validators import validate_rating

class RatingService:
    """Rating management service"""
    
    @staticmethod
    def create_rating(order_id, rater_id, ratee_id, rating, review_text=None, rating_type='courier'):
        """Create rating"""
        # Validate rating
        rating = validate_rating(rating)
        
        # Check order exists
        order = Order.query.get(order_id)
        if not order:
            raise NotFoundError(f'Order {order_id} not found')
        
        # Check if rating already exists
        existing_rating = Rating.query.filter_by(order_id=order_id, rater_id=rater_id).first()
        if existing_rating:
            raise ValidationError(f'You have already rated this order')
        
        # Create rating
        new_rating = Rating(
            order_id=order_id,
            rater_id=rater_id,
            ratee_id=ratee_id,
            rating=rating,
            review_text=review_text,
            rating_type=rating_type
        )
        
        db.session.add(new_rating)
        db.session.commit()
        
        return new_rating
    
    @staticmethod
    def get_ratings(user_id, limit=50, offset=0):
        """Get ratings for user"""
        ratings = Rating.query.filter_by(ratee_id=user_id).order_by(Rating.created_at.desc()).limit(limit).offset(offset).all()
        total = Rating.query.filter_by(ratee_id=user_id).count()
        return ratings, total
