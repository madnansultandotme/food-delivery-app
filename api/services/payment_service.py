from app import db
from models.payment import Payment, PaymentStatus, UserWallet, WalletTransaction
from models.order import Order
from utils.errors import NotFoundError, ValidationError
from utils.validators import validate_amount
from datetime import datetime

class PaymentService:
    """Payment management service"""
    
    @staticmethod
    def create_payment(order_id, user_id, amount, payment_method):
        """Create payment record"""
        # Validate amount
        amount = validate_amount(amount)
        
        # Check if order exists
        order = Order.query.get(order_id)
        if not order:
            raise NotFoundError(f'Order {order_id} not found')
        
        # Check if payment already exists
        existing_payment = Payment.query.filter_by(order_id=order_id).first()
        if existing_payment:
            raise ValidationError(f'Payment already exists for order {order_id}')
        
        # Create payment
        payment = Payment(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            status=PaymentStatus.PENDING.value
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return payment
    
    @staticmethod
    def process_payment(payment_id, transaction_id, gateway='stripe'):
        """Process payment"""
        payment = Payment.query.get(payment_id)
        if not payment:
            raise NotFoundError(f'Payment {payment_id} not found')
        
        payment.status = PaymentStatus.COMPLETED.value
        payment.transaction_id = transaction_id
        payment.gateway = gateway
        payment.processed_at = datetime.utcnow()
        
        db.session.commit()
        
        return payment
    
    @staticmethod
    def refund_payment(payment_id, reason):
        """Refund payment"""
        payment = Payment.query.get(payment_id)
        if not payment:
            raise NotFoundError(f'Payment {payment_id} not found')
        
        if payment.status != PaymentStatus.COMPLETED.value:
            raise ValidationError(f'Can only refund completed payments. Current status: {payment.status}')
        
        payment.status = PaymentStatus.REFUNDED.value
        payment.refunded_at = datetime.utcnow()
        payment.refund_reason = reason
        
        db.session.commit()
        
        return payment
    
    @staticmethod
    def get_or_create_wallet(user_id):
        """Get or create user wallet"""
        wallet = UserWallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            wallet = UserWallet(user_id=user_id, balance=0)
            db.session.add(wallet)
            db.session.commit()
        return wallet
    
    @staticmethod
    def add_wallet_balance(user_id, amount, description):
        """Add balance to wallet"""
        amount = validate_amount(amount)
        
        wallet = PaymentService.get_or_create_wallet(user_id)
        
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,
            transaction_type='credit',
            description=description,
            balance_before=wallet.balance,
            balance_after=wallet.balance + amount
        )
        
        wallet.balance += amount
        wallet.total_added += amount
        
        db.session.add(transaction)
        db.session.commit()
        
        return wallet, transaction
    
    @staticmethod
    def deduct_wallet_balance(user_id, amount, order_id, description):
        """Deduct balance from wallet"""
        amount = validate_amount(amount)
        
        wallet = PaymentService.get_or_create_wallet(user_id)
        
        if wallet.balance < amount:
            raise ValidationError('Insufficient wallet balance')
        
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            order_id=order_id,
            amount=amount,
            transaction_type='debit',
            description=description,
            balance_before=wallet.balance,
            balance_after=wallet.balance - amount
        )
        
        wallet.balance -= amount
        wallet.total_spent += amount
        
        db.session.add(transaction)
        db.session.commit()
        
        return wallet, transaction
