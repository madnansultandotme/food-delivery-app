from database import BaseModel, db
from enum import Enum

class PaymentStatus(Enum):
    """Payment statuses"""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class Payment(BaseModel):
    """Payment model"""
    __tablename__ = 'payments'
    
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False, unique=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default=PaymentStatus.PENDING.value)
    payment_method = db.Column(db.String(30), nullable=False)
    
    # Payment gateway details
    transaction_id = db.Column(db.String(100), unique=True, nullable=True)
    gateway = db.Column(db.String(50), nullable=True)  # stripe, razorpay, etc.
    
    # Metadata
    metadata = db.Column(db.JSON, nullable=True)
    
    # Timestamps
    processed_at = db.Column(db.DateTime, nullable=True)
    refunded_at = db.Column(db.DateTime, nullable=True)
    refund_reason = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': self.amount,
            'status': self.status,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat(),
        }

class UserWallet(BaseModel):
    """User wallet for storing balance"""
    __tablename__ = 'user_wallets'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    balance = db.Column(db.Float, default=0)
    total_added = db.Column(db.Float, default=0)
    total_spent = db.Column(db.Float, default=0)
    
    # Relationships
    transactions = db.relationship('WalletTransaction', backref='wallet', lazy=True, cascade='all, delete-orphan')

class WalletTransaction(BaseModel):
    """Wallet transaction history"""
    __tablename__ = 'wallet_transactions'
    
    wallet_id = db.Column(db.String(36), db.ForeignKey('user_wallets.id'), nullable=False)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=True)
    
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # credit, debit
    description = db.Column(db.Text, nullable=True)
    balance_before = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
