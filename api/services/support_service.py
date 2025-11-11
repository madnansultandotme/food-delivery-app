from api.models import SupportTicket, TicketStatus, User
from api.database import db
from api.utils.errors import NotFoundError, ValidationError
from api.utils.logger import get_logger
import uuid

logger = get_logger(__name__)

class SupportService:
    """Support ticket business logic"""
    
    @staticmethod
    def create_ticket(user_id, data):
        """Create support ticket"""
        ticket = SupportTicket(
            ticket_number=f"TKT{uuid.uuid4().hex[:10].upper()}",
            user_id=user_id,
            order_id=data.get('order_id'),
            subject=data.get('subject'),
            description=data.get('description'),
            category=data.get('category'),
            priority=data.get('priority', 'normal'),
            status=TicketStatus.OPEN
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        logger.info(f"Support ticket created: {ticket.ticket_number}")
        
        return ticket
    
    @staticmethod
    def update_ticket(ticket_id, data):
        """Update support ticket"""
        ticket = SupportTicket.query.get(ticket_id)
        if not ticket:
            raise NotFoundError('Support Ticket')
        
        if 'status' in data:
            ticket.status = TicketStatus[data['status'].upper()]
        
        if 'resolution' in data:
            ticket.resolution = data['resolution']
        
        if 'assigned_to' in data:
            ticket.assigned_to = data['assigned_to']
        
        db.session.commit()
        logger.info(f"Support ticket updated: {ticket_id}")
        
        return ticket
    
    @staticmethod
    def get_tickets(user_id=None, status=None, page=1, per_page=20):
        """Get support tickets"""
        query = SupportTicket.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=TicketStatus[status.upper()])
        
        tickets = query.paginate(page=page, per_page=per_page)
        return tickets
