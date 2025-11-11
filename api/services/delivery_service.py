from app import db
from models.delivery import Delivery, DeliveryStatus, DeliveryLocationHistory
from models.order import Order, OrderStatus
from utils.errors import NotFoundError, ValidationError
from utils.validators import validate_coordinates
from datetime import datetime
from sqlalchemy import and_

class DeliveryService:
    """Delivery management service"""
    
    @staticmethod
    def assign_delivery(order_id, courier_id):
        """Assign delivery to courier"""
        order = Order.query.get(order_id)
        if not order:
            raise NotFoundError(f'Order {order_id} not found')
        
        # Check if delivery already exists
        existing_delivery = Delivery.query.filter_by(order_id=order_id).first()
        if existing_delivery:
            raise ValidationError(f'Delivery already assigned for order {order_id}')
        
        # Create delivery
        delivery = Delivery(
            order_id=order_id,
            courier_id=courier_id,
            status=DeliveryStatus.ASSIGNED.value,
            assigned_at=datetime.utcnow()
        )
        
        db.session.add(delivery)
        db.session.flush()
        
        # Update order status
        order.status = OrderStatus.ASSIGNED.value
        
        db.session.commit()
        
        return delivery
    
    @staticmethod
    def update_delivery_location(delivery_id, latitude, longitude, accuracy=None, speed=None, heading=None, altitude=None):
        """Update delivery current location"""
        delivery = Delivery.query.get(delivery_id)
        if not delivery:
            raise NotFoundError(f'Delivery {delivery_id} not found')
        
        # Validate coordinates
        lat, lon = validate_coordinates(latitude, longitude)
        
        # Update current location
        delivery.current_latitude = lat
        delivery.current_longitude = lon
        
        db.session.flush()
        
        # Add to location history
        location_history = DeliveryLocationHistory(
            delivery_id=delivery_id,
            latitude=lat,
            longitude=lon,
            accuracy=accuracy,
            speed=speed,
            heading=heading,
            altitude=altitude
        )
        
        db.session.add(location_history)
        db.session.commit()
        
        return delivery
    
    @staticmethod
    def update_delivery_status(delivery_id, new_status):
        """Update delivery status"""
        delivery = Delivery.query.get(delivery_id)
        if not delivery:
            raise NotFoundError(f'Delivery {delivery_id} not found')
        
        # Validate status
        valid_statuses = [s.value for s in DeliveryStatus]
        if new_status not in valid_statuses:
            raise ValidationError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
        
        delivery.status = new_status
        
        # Update timestamps based on status
        if new_status == DeliveryStatus.PICKED_UP.value:
            delivery.pickup_at = datetime.utcnow()
        elif new_status == DeliveryStatus.DELIVERED.value:
            delivery.delivery_at = datetime.utcnow()
        
        # Update order status accordingly
        order = delivery.order
        if new_status == DeliveryStatus.IN_TRANSIT.value:
            order.status = OrderStatus.IN_TRANSIT.value
        elif new_status == DeliveryStatus.DELIVERED.value:
            order.status = OrderStatus.DELIVERED.value
        
        db.session.commit()
        
        return delivery
    
    @staticmethod
    def get_courier_active_deliveries(courier_id):
        """Get active deliveries for courier"""
        active_statuses = [
            DeliveryStatus.ASSIGNED.value,
            DeliveryStatus.PICKED_UP.value,
            DeliveryStatus.IN_TRANSIT.value
        ]
        
        deliveries = Delivery.query.filter(
            and_(
                Delivery.courier_id == courier_id,
                Delivery.status.in_(active_statuses)
            )
        ).all()
        
        return deliveries
    
    @staticmethod
    def get_delivery_tracking(delivery_id):
        """Get delivery tracking information"""
        delivery = Delivery.query.get(delivery_id)
        if not delivery:
            raise NotFoundError(f'Delivery {delivery_id} not found')
        
        location_history = DeliveryLocationHistory.query.filter_by(delivery_id=delivery_id).order_by(
            DeliveryLocationHistory.created_at.desc()
        ).all()
        
        return {
            'delivery': delivery,
            'location_history': location_history
        }
