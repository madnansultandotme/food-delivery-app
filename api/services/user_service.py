from app import db
from models.user import User, UserRole
from utils.errors import NotFoundError, ValidationError
from utils.validators import validate_email, validate_coordinates
from datetime import datetime

class UserService:
    """User management service"""
    
    @staticmethod
    def get_user(user_id):
        """Get user by ID"""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError(f'User {user_id} not found')
        return user
    
    @staticmethod
    def update_profile(user_id, **kwargs):
        """Update user profile"""
        user = UserService.get_user(user_id)
        
        # Allowed fields to update
        allowed_fields = ['first_name', 'last_name', 'phone', 'address', 'profile_picture']
        
        for field, value in kwargs.items():
            if field not in allowed_fields:
                continue
            
            if field == 'phone':
                if len(str(value)) < 10:
                    raise ValidationError('Invalid phone number')
            
            setattr(user, field, value)
        
        db.session.commit()
        return user
    
    @staticmethod
    def update_location(user_id, latitude, longitude):
        """Update user location"""
        user = UserService.get_user(user_id)
        
        lat, lon = validate_coordinates(latitude, longitude)
        
        user.latitude = lat
        user.longitude = lon
        
        db.session.commit()
        return user
    
    @staticmethod
    def get_courier_stats(courier_id):
        """Get courier statistics"""
        from models.delivery import Delivery, DeliveryStatus
        from models.rating import Rating
        from sqlalchemy import func
        
        user = UserService.get_user(courier_id)
        
        # Total deliveries
        total_deliveries = Delivery.query.filter_by(courier_id=courier_id).count()
        
        # Completed deliveries
        completed_deliveries = Delivery.query.filter_by(
            courier_id=courier_id,
            status=DeliveryStatus.DELIVERED.value
        ).count()
        
        # Average rating
        ratings = db.session.query(func.avg(Rating.rating)).filter_by(ratee_id=courier_id).scalar()
        average_rating = float(ratings) if ratings else 0
        
        # Total reviews
        total_reviews = Rating.query.filter_by(ratee_id=courier_id).count()
        
        return {
            'total_deliveries': total_deliveries,
            'completed_deliveries': completed_deliveries,
            'average_rating': round(average_rating, 2),
            'total_reviews': total_reviews,
            'success_rate': round((completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0, 2)
        }
    
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate user account"""
        user = UserService.get_user(user_id)
        user.is_active = False
        db.session.commit()
        return user
    
    @staticmethod
    def activate_user(user_id):
        """Activate user account"""
        user = UserService.get_user(user_id)
        user.is_active = True
        db.session.commit()
        return user
