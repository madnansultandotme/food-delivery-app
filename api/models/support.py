from database import BaseModel, db
from enum import Enum

class TicketStatus(Enum):
    """Support ticket status"""
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    CLOSED = 'closed'
    REOPENED = 'reopened'

class TicketPriority(Enum):
    """Support ticket priority"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class SupportTicket(BaseModel):
    """Support ticket model"""
    __tablename__ = 'support_tickets'
    
    ticket_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=True)
    
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    status = db.Column(db.String(20), default=TicketStatus.OPEN.value)
    priority = db.Column(db.String(20), default=TicketPriority.MEDIUM.value)
    
    assigned_to = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    messages = db.relationship('TicketMessage', backref='ticket', lazy=True, cascade='all, delete-orphan')

class TicketMessage(BaseModel):
    """Support ticket messages"""
    __tablename__ = 'ticket_messages'
    
    ticket_id = db.Column(db.String(36), db.ForeignKey('support_tickets.id'), nullable=False)
    sent_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    attachment = db.Column(db.String(255), nullable=True)
