from app import db
from models.order import Order, OrderStatus, OrderStatusHistory, PaymentMethod
from models.user import User
from utils.errors import NotFoundError, ValidationError
from utils.validators import validate_coordinates, validate_amount
from datetime import datetime, timedelta
import uuid

class OrderService:
    """Order management service"""
    
    @staticmethod
    def create_order(customer_id, pickup_address, delivery_address, package_details, pricing, payment_method='card'):
        """Create new order"""
        # Validate payment method
        valid_methods = [m.value for m in PaymentMethod]
        if payment_method not in valid_methods:
            raise ValidationError(f'Invalid payment method. Must be one of: {", ".join(valid_methods)}')
        
        # Validate pricing
        total_amount = validate_amount(pricing.get('total_amount', 0))
        
        # Generate order number
        order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create order
        order = Order(
            order_number=order_number,
            customer_id=customer_id,
            pickup_address=pickup_address['address'],
            pickup_latitude=pickup_address['latitude'],
            pickup_longitude=pickup_address['longitude'],
            pickup_contact=pickup_address['contact'],
            pickup_phone=pickup_address['phone'],
            delivery_address=delivery_address['address'],
            delivery_latitude=delivery_address['latitude'],
            delivery_longitude=delivery_address['longitude'],
            delivery_contact=delivery_address['contact'],
            delivery_phone=delivery_address['phone'],
            package_description=package_details['description'],
            package_weight=float(package_details['weight']),
            package_dimensions=package_details.get('dimensions'),
            special_instructions=package_details.get('special_instructions'),
            base_fare=validate_amount(pricing.get('base_fare', 0)),
            distance_fare=validate_amount(pricing.get('distance_fare', 0)),
            surcharge=validate_amount(pricing.get('surcharge', 0)),
            discount=validate_amount(pricing.get('discount', 0)),
            total_amount=total_amount,
            payment_method=payment_method,
            estimated_delivery_time=datetime.utcnow() + timedelta(hours=3),
        )
        
        db.session.add(order)
        db.session.flush()
        
        # Log status change
        OrderService._log_status_change(order.id, None, OrderStatus.PENDING.value, customer_id, 'Order created')
        
        db.session.commit()
        
        return order
    
    @staticmethod
    def update_order_status(order_id, new_status, changed_by_id, reason=None):
        """Update order status"""
        order = Order.query.get(order_id)
        if not order:
            raise NotFoundError(f'Order {order_id} not found')
        
        # Validate status
        valid_statuses = [s.value for s in OrderStatus]
        if new_status not in valid_statuses:
            raise ValidationError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
        
        old_status = order.status
        order.status = new_status
        
        # Update timestamps based on status
        if new_status == OrderStatus.IN_TRANSIT.value:
            order.pickup_time = datetime.utcnow()
        elif new_status == OrderStatus.DELIVERED.value:
            order.delivery_time = datetime.utcnow()
        elif new_status == OrderStatus.CANCELLED.value:
            order.cancelled_at = datetime.utcnow()
            order.cancellation_reason = reason
        
        db.session.flush()
        
        # Log status change
        OrderService._log_status_change(order.id, old_status, new_status, changed_by_id, reason)
        
        db.session.commit()
        
        return order
    
    @staticmethod
    def _log_status_change(order_id, from_status, to_status, changed_by_id, reason=None):
        """Log order status change"""
        history = OrderStatusHistory(
            order_id=order_id,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by_id,
            reason=reason
        )
        db.session.add(history)
    
    @staticmethod
    def get_order(order_id):
        """Get order by ID"""
        order = Order.query.get(order_id)
        if not order:
            raise NotFoundError(f'Order {order_id} not found')
        return order
    
    @staticmethod
    def get_customer_orders(customer_id, limit=50, offset=0):
        """Get customer's orders"""
        orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).limit(limit).offset(offset).all()
        total = Order.query.filter_by(customer_id=customer_id).count()
        return orders, total
    
    @staticmethod
    def cancel_order(order_id, cancellation_reason):
        """Cancel order"""
        order = OrderService.get_order(order_id)
        
        if order.status in [OrderStatus.DELIVERED.value, OrderStatus.CANCELLED.value]:
            raise ValidationError(f'Cannot cancel order with status {order.status}')
        
        return OrderService.update_order_status(order_id, OrderStatus.CANCELLED.value, None, cancellation_reason)
