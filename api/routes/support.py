from flask import Blueprint, request, jsonify
from utils.decorators import require_auth, validate_json, require_role
from utils.errors import ValidationError, NotFoundError
from models.support import SupportTicket, TicketMessage, TicketStatus, TicketPriority
from models.user import UserRole
from app import db
import logging
import uuid

support_bp = Blueprint('support', __name__)
logger = logging.getLogger(__name__)

@support_bp.route('/tickets', methods=['POST'])
@require_auth
@validate_json('subject', 'description')
def create_ticket():
    """Create support ticket"""
    try:
        data = request.data
        
        ticket_number = f"TICKET-{uuid.uuid4().hex[:8].upper()}"
        
        ticket = SupportTicket(
            ticket_number=ticket_number,
            user_id=request.user.id,
            order_id=data.get('order_id'),
            subject=data['subject'],
            description=data['description'],
            priority=data.get('priority', TicketPriority.MEDIUM.value)
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Ticket created successfully',
            'ticket': {
                'id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'subject': ticket.subject,
                'status': ticket.status,
                'created_at': ticket.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        logger.error(f"Create ticket error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@support_bp.route('/tickets/<ticket_id>', methods=['GET'])
@require_auth
def get_ticket(ticket_id):
    """Get ticket details"""
    try:
        ticket = SupportTicket.query.get(ticket_id)
        if not ticket:
            raise NotFoundError(f'Ticket {ticket_id} not found')
        
        return jsonify({
            'success': True,
            'ticket': {
                'id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'subject': ticket.subject,
                'description': ticket.description,
                'status': ticket.status,
                'priority': ticket.priority,
                'messages': [
                    {
                        'id': m.id,
                        'sent_by': m.sent_by,
                        'message': m.message,
                        'created_at': m.created_at.isoformat()
                    } for m in ticket.messages
                ],
                'created_at': ticket.created_at.isoformat()
            }
        }), 200
    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Get ticket error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@support_bp.route('/tickets/<ticket_id>/messages', methods=['POST'])
@require_auth
@validate_json('message')
def add_message(ticket_id):
    """Add message to ticket"""
    try:
        data = request.data
        
        ticket = SupportTicket.query.get(ticket_id)
        if not ticket:
            raise NotFoundError(f'Ticket {ticket_id} not found')
        
        message = TicketMessage(
            ticket_id=ticket_id,
            sent_by=request.user.id,
            message=data['message']
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message added successfully'
        }), 201
    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Add message error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@support_bp.route('/tickets/<ticket_id>/status', methods=['PUT'])
@require_auth
@require_role(UserRole.ADMIN.value)
@validate_json('status')
def update_ticket_status(ticket_id):
    """Update ticket status"""
    try:
        data = request.data
        
        ticket = SupportTicket.query.get(ticket_id)
        if not ticket:
            raise NotFoundError(f'Ticket {ticket_id} not found')
        
        ticket.status = data['status']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Ticket status updated'
        }), 200
    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Update ticket status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
