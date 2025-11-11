import os
import jwt
import json
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from flask import Flask, request, jsonify
from flask_cors import CORS
from decimal import Decimal

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = 'HS256'
DB_URL = os.getenv('SUPABASE_POSTGRES_URL')

# Database connection
def get_db_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20) UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'customer',
                address TEXT,
                city VARCHAR(100),
                country VARCHAR(100),
                latitude FLOAT,
                longitude FLOAT,
                profile_picture_url TEXT,
                is_verified BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Orders table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                order_number VARCHAR(50) UNIQUE NOT NULL,
                customer_id INTEGER NOT NULL REFERENCES users(id),
                courier_id INTEGER REFERENCES users(id),
                pickup_address TEXT NOT NULL,
                delivery_address TEXT NOT NULL,
                pickup_latitude FLOAT,
                pickup_longitude FLOAT,
                delivery_latitude FLOAT,
                delivery_longitude FLOAT,
                package_description TEXT,
                package_weight FLOAT,
                package_dimensions TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                payment_status VARCHAR(50) DEFAULT 'pending',
                estimated_delivery TIMESTAMP,
                actual_delivery TIMESTAMP,
                total_amount DECIMAL(10, 2),
                delivery_fee DECIMAL(10, 2),
                distance_km FLOAT,
                special_instructions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Order status history table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS order_status_history (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                status VARCHAR(50) NOT NULL,
                notes TEXT,
                location_latitude FLOAT,
                location_longitude FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ratings and reviews table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                reviewer_id INTEGER NOT NULL REFERENCES users(id),
                reviewee_id INTEGER NOT NULL REFERENCES users(id),
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                review_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Payments table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id),
                amount DECIMAL(10, 2) NOT NULL,
                payment_method VARCHAR(50) NOT NULL,
                transaction_id VARCHAR(255),
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Support tickets table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS support_tickets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                order_id INTEGER REFERENCES orders(id),
                subject VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'open',
                priority VARCHAR(50) DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Promotional codes table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS promo_codes (
                id SERIAL PRIMARY KEY,
                code VARCHAR(50) UNIQUE NOT NULL,
                discount_type VARCHAR(50),
                discount_value DECIMAL(10, 2),
                max_uses INTEGER,
                current_uses INTEGER DEFAULT 0,
                valid_from TIMESTAMP,
                valid_until TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("Database tables initialized successfully")
    except Exception as e:
        conn.rollback()
        print(f"Database initialization error: {e}")
    finally:
        cur.close()
        conn.close()

# Utility functions
def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hash_):
    """Verify password"""
    return bcrypt.checkpw(password.encode('utf-8'), hash_.encode('utf-8'))

def create_token(user_id, role, expires_in_days=30):
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=expires_in_days)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def token_required(f):
    """JWT token verification decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            kwargs['user_id'] = payload['user_id']
            kwargs['user_role'] = payload['role']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Admin role verification decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_role = kwargs.get('user_role')
        if user_role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

# ========== AUTHENTICATION ENDPOINTS ==========

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    required_fields = ['name', 'email', 'phone', 'password', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if data['role'] not in ['customer', 'courier', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        password_hash = hash_password(data['password'])
        
        cur.execute('''
            INSERT INTO users (name, email, phone, password_hash, role, address, city, country)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, name, email, role
        ''', (data['name'], data['email'], data['phone'], password_hash, 
              data['role'], data.get('address'), data.get('city'), data.get('country')))
        
        user = cur.fetchone()
        conn.commit()
        
        token = create_token(user[0], user[3])
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'role': user[3]
            },
            'token': token
        }), 201
    
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Email or phone already exists'}), 409
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute('SELECT id, name, email, role, password_hash FROM users WHERE email = %s', 
                   (data['email'],))
        user = cur.fetchone()
        
        if not user or not verify_password(data['password'], user['password_hash']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = create_token(user['id'], user['role'])
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            },
            'token': token
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ========== USER ENDPOINTS ==========

@app.route('/api/users/profile', methods=['GET'])
@token_required
def get_profile(user_id, user_role):
    """Get user profile"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute('''
            SELECT id, name, email, phone, role, address, city, country, 
                   latitude, longitude, profile_picture_url, is_verified, created_at
            FROM users WHERE id = %s
        ''', (user_id,))
        
        user = cur.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': dict(user)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/users/profile', methods=['PUT'])
@token_required
def update_profile(user_id, user_role):
    """Update user profile"""
    data = request.get_json()
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Build dynamic update query
        fields = []
        values = []
        
        for field in ['name', 'phone', 'address', 'city', 'country', 'latitude', 'longitude', 'profile_picture_url']:
            if field in data:
                fields.append(f"{field} = %s")
                values.append(data[field])
        
        if not fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *"
        cur.execute(query, values)
        
        user = cur.fetchone()
        conn.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': dict(user)
        }), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ========== ORDER ENDPOINTS ==========

@app.route('/api/orders', methods=['POST'])
@token_required
def create_order(user_id, user_role):
    """Create a new order"""
    if user_role != 'customer':
        return jsonify({'error': 'Only customers can create orders'}), 403
    
    data = request.get_json()
    
    required_fields = ['pickup_address', 'delivery_address', 'package_description']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id}"
        
        cur.execute('''
            INSERT INTO orders (
                order_number, customer_id, pickup_address, delivery_address,
                pickup_latitude, pickup_longitude, delivery_latitude, delivery_longitude,
                package_description, package_weight, package_dimensions,
                delivery_fee, total_amount, special_instructions
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        ''', (
            order_number, user_id, data['pickup_address'], data['delivery_address'],
            data.get('pickup_latitude'), data.get('pickup_longitude'),
            data.get('delivery_latitude'), data.get('delivery_longitude'),
            data['package_description'], data.get('package_weight'),
            data.get('package_dimensions'), data.get('delivery_fee', 50),
            data.get('total_amount', 50), data.get('special_instructions')
        ))
        
        order = cur.fetchone()
        
        # Log initial status
        cur.execute('''
            INSERT INTO order_status_history (order_id, status, notes)
            VALUES (%s, %s, %s)
        ''', (order['id'], 'pending', 'Order created'))
        
        conn.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order': dict(order)
        }), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(order_id, user_id, user_role):
    """Get order details"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
        order = cur.fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check authorization
        if user_role != 'admin' and order['customer_id'] != user_id and order['courier_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get status history
        cur.execute('SELECT * FROM order_status_history WHERE order_id = %s ORDER BY created_at', (order_id,))
        history = cur.fetchall()
        
        return jsonify({
            'order': dict(order),
            'status_history': [dict(h) for h in history]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/orders', methods=['GET'])
@token_required
def list_orders(user_id, user_role):
    """List orders based on user role"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        status = request.args.get('status')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if user_role == 'customer':
            query = 'SELECT * FROM orders WHERE customer_id = %s'
            params = [user_id]
        elif user_role == 'courier':
            query = 'SELECT * FROM orders WHERE courier_id = %s'
            params = [user_id]
        else:  # admin
            query = 'SELECT * FROM orders WHERE 1=1'
            params = []
        
        if status:
            query += ' AND status = %s'
            params.append(status)
        
        query += ' ORDER BY created_at DESC LIMIT %s OFFSET %s'
        params.extend([limit, offset])
        
        cur.execute(query, params)
        orders = cur.fetchall()
        
        return jsonify({
            'orders': [dict(o) for o in orders]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/orders/<int:order_id>/assign', methods=['PUT'])
@token_required
@admin_required
def assign_courier(order_id, user_id, user_role):
    """Assign a courier to an order"""
    data = request.get_json()
    
    if not data.get('courier_id'):
        return jsonify({'error': 'Courier ID required'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Verify courier exists and has correct role
        cur.execute('SELECT id FROM users WHERE id = %s AND role = %s', 
                   (data['courier_id'], 'courier'))
        if not cur.fetchone():
            return jsonify({'error': 'Courier not found'}), 404
        
        cur.execute('''
            UPDATE orders 
            SET courier_id = %s, status = 'assigned', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        ''', (data['courier_id'], order_id))
        
        order = cur.fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Log status change
        cur.execute('''
            INSERT INTO order_status_history (order_id, status, notes)
            VALUES (%s, %s, %s)
        ''', (order_id, 'assigned', f"Assigned to courier {data['courier_id']}"))
        
        conn.commit()
        
        return jsonify({
            'message': 'Courier assigned successfully',
            'order': dict(order)
        }), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
@token_required
def update_order_status(order_id, user_id, user_role):
    """Update order status"""
    data = request.get_json()
    
    if not data.get('status'):
        return jsonify({'error': 'Status required'}), 400
    
    valid_statuses = ['pending', 'assigned', 'picked_up', 'in_transit', 'delivered', 'cancelled']
    if data['status'] not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
        order = cur.fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check authorization
        if user_role != 'admin' and order['courier_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Update order
        query = 'UPDATE orders SET status = %s, updated_at = CURRENT_TIMESTAMP'
        params = [data['status']]
        
        # Set delivery time if delivered
        if data['status'] == 'delivered':
            query += ', actual_delivery = CURRENT_TIMESTAMP, payment_status = %s'
            params.append('completed')
        
        query += ' WHERE id = %s RETURNING *'
        params.append(order_id)
        
        cur.execute(query, params)
        updated_order = cur.fetchone()
        
        # Log status change
        cur.execute('''
            INSERT INTO order_status_history (order_id, status, notes, location_latitude, location_longitude)
            VALUES (%s, %s, %s, %s, %s)
        ''', (order_id, data['status'], data.get('notes', ''),
              data.get('latitude'), data.get('longitude')))
        
        conn.commit()
        
        return jsonify({
            'message': 'Order status updated',
            'order': dict(updated_order)
        }), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ========== RATINGS ENDPOINTS ==========

@app.route('/api/orders/<int:order_id>/rate', methods=['POST'])
@token_required
def rate_delivery(order_id, user_id, user_role):
    """Rate a completed order"""
    data = request.get_json()
    
    if not data.get('rating') or not data.get('reviewee_id'):
        return jsonify({'error': 'Rating and reviewee_id required'}), 400
    
    if not 1 <= data['rating'] <= 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Verify order exists and belongs to user
        cur.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
        order = cur.fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order['customer_id'] != user_id and order['courier_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Create rating
        cur.execute('''
            INSERT INTO ratings (order_id, reviewer_id, reviewee_id, rating, review_text)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        ''', (order_id, user_id, data['reviewee_id'], data['rating'], data.get('review_text')))
        
        rating = cur.fetchone()
        conn.commit()
        
        return jsonify({
            'message': 'Rating submitted successfully',
            'rating': dict(rating)
        }), 201
    
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Rating already exists for this order'}), 409
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/users/<int:user_id>/ratings', methods=['GET'])
def get_user_ratings(user_id):
    """Get ratings for a user"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute('''
            SELECT AVG(rating) as average_rating, COUNT(*) as total_ratings
            FROM ratings WHERE reviewee_id = %s
        ''', (user_id,))
        
        stats = cur.fetchone()
        
        cur.execute('''
            SELECT * FROM ratings WHERE reviewee_id = %s ORDER BY created_at DESC
        ''', (user_id,))
        
        ratings = cur.fetchall()
        
        return jsonify({
            'stats': dict(stats),
            'ratings': [dict(r) for r in ratings]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ========== PAYMENT ENDPOINTS ==========

@app.route('/api/payments', methods=['POST'])
@token_required
def create_payment(user_id, user_role):
    """Create a payment"""
    data = request.get_json()
    
    required_fields = ['order_id', 'amount', 'payment_method']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Verify order exists
        cur.execute('SELECT * FROM orders WHERE id = %s', (data['order_id'],))
        order = cur.fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order['customer_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Create payment
        cur.execute('''
            INSERT INTO payments (order_id, user_id, amount, payment_method, transaction_id, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        ''', (data['order_id'], user_id, data['amount'], data['payment_method'],
              data.get('transaction_id', ''), 'completed'))
        
        payment = cur.fetchone()
        
        # Update order payment status
        cur.execute('''
            UPDATE orders SET payment_status = 'completed'
            WHERE id = %s
        ''', (data['order_id'],))
        
        conn.commit()
        
        return jsonify({
            'message': 'Payment recorded successfully',
            'payment': dict(payment)
        }), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/payments/<int:order_id>', methods=['GET'])
@token_required
def get_payment(order_id, user_id, user_role):
    """Get payment details for an order"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Verify order exists
        cur.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
        order = cur.fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if user_role != 'admin' and order['customer_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        cur.execute('SELECT * FROM payments WHERE order_id = %s', (order_id,))
        payment = cur.fetchone()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        return jsonify({
            'payment': dict(payment)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ========== DELIVERY TRACKING ENDPOINTS ==========

@app.route('/api/orders/<int:order_id>/tracking', methods=['GET'])
@token_required
def get_tracking(order_id, user_id, user_role):
    """Get real-time tracking for an order"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute('''
            SELECT id, order_number, status, pickup_latitude, pickup_longitude,
                   delivery_latitude, delivery_longitude, courier_id, estimated_delivery
            FROM orders WHERE id = %s
        ''', (order_id,))
        
        order = cur.fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Get courier current location (latest status history)
        cur.execute('''
            SELECT location_latitude, location_longitude, created_at
            FROM order_status_history
            WHERE order_id = %s AND location_latitude IS NOT NULL
            ORDER BY created_at DESC LIMIT 1
        ''', (order_id,))
        
        current_location = cur.fetchone()
        
        return jsonify({
            'order': dict(order),
            'current_location': dict(current_location) if current_location else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ========== ADMIN ENDPOINTS ==========

@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
def list_all_users(user_id, user_role):
    """List all users (admin only)"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        role = request.args.get('role')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = 'SELECT id, name, email, phone, role, is_verified, is_active, created_at FROM users WHERE 1=1'
        params = []
        
        if role:
            query += ' AND role = %s'
            params.append(role)
        
        query += ' ORDER BY created_at DESC LIMIT %s OFFSET %s'
        params.extend([limit, offset])
        
        cur.execute(query, params)
        users = cur.fetchall()
        
        return jsonify({
            'users': [dict(u) for u in users]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/admin/orders', methods=['GET'])
@token_required
@admin_required
def list_all_orders(user_id, user_role):
    """List all orders (admin only)"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = 'SELECT * FROM orders WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = %s'
            params.append(status)
        
        query += ' ORDER BY created_at DESC LIMIT %s OFFSET %s'
        params.extend([limit, offset])
        
        cur.execute(query, params)
        orders = cur.fetchall()
        
        return jsonify({
            'orders': [dict(o) for o in orders]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/admin/statistics', methods=['GET'])
@token_required
@admin_required
def get_statistics(user_id, user_role):
    """Get platform statistics (admin only)"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Total orders
        cur.execute('SELECT COUNT(*) as total FROM orders')
        total_orders = cur.fetchone()['total']
        
        # Completed orders
        cur.execute("SELECT COUNT(*) as total FROM orders WHERE status = 'delivered'")
        completed_orders = cur.fetchone()['total']
        
        # Total revenue
        cur.execute('SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE status = %s', 
                   ('completed',))
        revenue = cur.fetchone()['total']
        
        # Total users
        cur.execute('SELECT COUNT(*) as total FROM users')
        total_users = cur.fetchone()['total']
        
        # Active couriers
        cur.execute("SELECT COUNT(*) as total FROM users WHERE role = 'courier' AND is_active = true")
        active_couriers = cur.fetchone()['total']
        
        return jsonify({
            'statistics': {
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'total_revenue': float(revenue),
                'total_users': total_users,
                'active_couriers': active_couriers
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ========== SUPPORT ENDPOINTS ==========

@app.route('/api/support/tickets', methods=['POST'])
@token_required
def create_support_ticket(user_id, user_role):
    """Create a support ticket"""
    data = request.get_json()
    
    required_fields = ['subject', 'description']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute('''
            INSERT INTO support_tickets (user_id, order_id, subject, description, status, priority)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        ''', (user_id, data.get('order_id'), data['subject'], data['description'],
              'open', data.get('priority', 'medium')))
        
        ticket = cur.fetchone()
        conn.commit()
        
        return jsonify({
            'message': 'Support ticket created',
            'ticket': dict(ticket)
        }), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/support/tickets', methods=['GET'])
@token_required
def list_support_tickets(user_id, user_role):
    """List support tickets"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if user_role == 'admin':
            cur.execute('SELECT * FROM support_tickets ORDER BY created_at DESC')
        else:
            cur.execute('SELECT * FROM support_tickets WHERE user_id = %s ORDER BY created_at DESC', 
                       (user_id,))
        
        tickets = cur.fetchall()
        
        return jsonify({
            'tickets': [dict(t) for t in tickets]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ========== PROMO CODE ENDPOINTS ==========

@app.route('/api/promo-codes/validate', methods=['POST'])
@token_required
def validate_promo_code(user_id, user_role):
    """Validate and apply promo code"""
    data = request.get_json()
    
    if not data.get('code'):
        return jsonify({'error': 'Code required'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute('''
            SELECT * FROM promo_codes 
            WHERE code = %s AND is_active = true 
            AND valid_from <= CURRENT_TIMESTAMP 
            AND valid_until >= CURRENT_TIMESTAMP
        ''', (data['code'],))
        
        promo = cur.fetchone()
        
        if not promo:
            return jsonify({'error': 'Invalid or expired promo code'}), 404
        
        if promo['max_uses'] and promo['current_uses'] >= promo['max_uses']:
            return jsonify({'error': 'Promo code usage limit reached'}), 400
        
        return jsonify({
            'message': 'Promo code is valid',
            'discount_type': promo['discount_type'],
            'discount_value': float(promo['discount_value'])
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# ========== HEALTH CHECK ==========

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Initialize database on startup
if __name__ == '__main__':
    init_db()
    app.run(debug=False)
