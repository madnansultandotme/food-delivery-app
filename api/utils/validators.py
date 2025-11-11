import re
from utils.errors import ValidationError

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError('Invalid email format')
    return email

def validate_phone(phone):
    """Validate phone number"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    if len(digits) < 10:
        raise ValidationError('Phone number must have at least 10 digits')
    return phone

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password must contain at least one digit')
    return password

def validate_coordinates(latitude, longitude):
    """Validate GPS coordinates"""
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        if not (-90 <= lat <= 90):
            raise ValidationError('Latitude must be between -90 and 90')
        if not (-180 <= lon <= 180):
            raise ValidationError('Longitude must be between -180 and 180')
        
        return lat, lon
    except (TypeError, ValueError):
        raise ValidationError('Invalid coordinates format')

def validate_rating(rating):
    """Validate rating value"""
    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            raise ValidationError('Rating must be between 1 and 5')
        return rating
    except (TypeError, ValueError):
        raise ValidationError('Rating must be an integer between 1 and 5')

def validate_amount(amount):
    """Validate currency amount"""
    try:
        amount = float(amount)
        if amount < 0:
            raise ValidationError('Amount cannot be negative')
        return round(amount, 2)
    except (TypeError, ValueError):
        raise ValidationError('Invalid amount format')
