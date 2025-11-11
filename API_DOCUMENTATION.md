# Courier Delivery API Documentation

## Base URL
\`\`\`
https://your-app.vercel.app/api
\`\`\`

## Authentication
All endpoints (except `/auth/register` and `/auth/login`) require a JWT token in the `Authorization` header:
\`\`\`
Authorization: Bearer <your-jwt-token>
\`\`\`

---

## Authentication Endpoints

### Register User
**POST** `/auth/register`
\`\`\`json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "password": "secure_password",
  "role": "customer|courier|admin",
  "address": "123 Main St",
  "city": "New York",
  "country": "USA"
}
\`\`\`
**Response:** `201 Created`
\`\`\`json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "customer"
  },
  "token": "eyJ..."
}
\`\`\`

### Login
**POST** `/auth/login`
\`\`\`json
{
  "email": "john@example.com",
  "password": "secure_password"
}
\`\`\`
**Response:** `200 OK`
\`\`\`json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "customer"
  },
  "token": "eyJ..."
}
\`\`\`

---

## User Endpoints

### Get User Profile
**GET** `/users/profile`
**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
\`\`\`json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "role": "customer",
    "address": "123 Main St",
    "city": "New York",
    "country": "USA",
    "is_verified": false,
    "created_at": "2024-01-01T12:00:00"
  }
}
\`\`\`

### Update User Profile
**PUT** `/users/profile`
**Headers:** `Authorization: Bearer <token>`
\`\`\`json
{
  "name": "Jane Doe",
  "phone": "+9876543210",
  "address": "456 Oak Ave",
  "latitude": 40.7128,
  "longitude": -74.0060
}
\`\`\`

---

## Order Endpoints

### Create Order
**POST** `/orders`
**Headers:** `Authorization: Bearer <token>`
\`\`\`json
{
  "pickup_address": "123 Main St, New York",
  "delivery_address": "456 Oak Ave, New York",
  "pickup_latitude": 40.7128,
  "pickup_longitude": -74.0060,
  "delivery_latitude": 40.7580,
  "delivery_longitude": -73.9855,
  "package_description": "Documents",
  "package_weight": 0.5,
  "package_dimensions": "10x10x2",
  "delivery_fee": 50,
  "special_instructions": "Leave at door"
}
\`\`\`
**Response:** `201 Created`

### Get Order Details
**GET** `/orders/<order_id>`
**Headers:** `Authorization: Bearer <token>`

### List Orders
**GET** `/orders?status=pending&limit=20&offset=0`
**Headers:** `Authorization: Bearer <token>`

### Update Order Status
**PUT** `/orders/<order_id>/status`
**Headers:** `Authorization: Bearer <token>`
\`\`\`json
{
  "status": "in_transit|delivered|cancelled",
  "notes": "On the way",
  "latitude": 40.7200,
  "longitude": -73.9900
}
\`\`\`

### Assign Courier to Order
**PUT** `/orders/<order_id>/assign` (Admin only)
**Headers:** `Authorization: Bearer <token>`
\`\`\`json
{
  "courier_id": 5
}
\`\`\`

---

## Tracking Endpoints

### Get Real-time Tracking
**GET** `/orders/<order_id>/tracking`
**Headers:** `Authorization: Bearer <token>`

**Response:**
\`\`\`json
{
  "order": {
    "id": 1,
    "order_number": "ORD-20240101120000-1",
    "status": "in_transit",
    "pickup_latitude": 40.7128,
    "pickup_longitude": -74.0060,
    "delivery_latitude": 40.7580,
    "delivery_longitude": -73.9855,
    "courier_id": 5,
    "estimated_delivery": "2024-01-01T15:00:00"
  },
  "current_location": {
    "location_latitude": 40.7300,
    "location_longitude": -73.9950,
    "created_at": "2024-01-01T14:30:00"
  }
}
\`\`\`

---

## Ratings Endpoints

### Rate Delivery
**POST** `/orders/<order_id>/rate`
**Headers:** `Authorization: Bearer <token>`
\`\`\`json
{
  "rating": 5,
  "reviewee_id": 5,
  "review_text": "Great service, very fast delivery!"
}
\`\`\`
**Response:** `201 Created`

### Get User Ratings
**GET** `/users/<user_id>/ratings`

**Response:**
\`\`\`json
{
  "stats": {
    "average_rating": 4.8,
    "total_ratings": 25
  },
  "ratings": [
    {
      "id": 1,
      "order_id": 1,
      "reviewer_id": 1,
      "reviewee_id": 5,
      "rating": 5,
      "review_text": "Great service!",
      "created_at": "2024-01-01T16:00:00"
    }
  ]
}
\`\`\`

---

## Payment Endpoints

### Create Payment
**POST** `/payments`
**Headers:** `Authorization: Bearer <token>`
\`\`\`json
{
  "order_id": 1,
  "amount": 50.00,
  "payment_method": "card|wallet|cash",
  "transaction_id": "txn_123456"
}
\`\`\`
**Response:** `201 Created`

### Get Payment Details
**GET** `/payments/<order_id>`
**Headers:** `Authorization: Bearer <token>`

---

## Admin Endpoints

### List All Users
**GET** `/admin/users?role=courier&limit=20&offset=0`
**Headers:** `Authorization: Bearer <token>` (Admin only)

### List All Orders
**GET** `/admin/orders?status=pending&limit=50&offset=0`
**Headers:** `Authorization: Bearer <token>` (Admin only)

### Get Platform Statistics
**GET** `/admin/statistics`
**Headers:** `Authorization: Bearer <token>` (Admin only)

**Response:**
\`\`\`json
{
  "statistics": {
    "total_orders": 150,
    "completed_orders": 145,
    "total_revenue": 7250.50,
    "total_users": 300,
    "active_couriers": 45
  }
}
\`\`\`

---

## Support Endpoints

### Create Support Ticket
**POST** `/support/tickets`
**Headers:** `Authorization: Bearer <token>`
\`\`\`json
{
  "subject": "Delivery Issue",
  "description": "Package not delivered",
  "order_id": 1,
  "priority": "high|medium|low"
}
\`\`\`

### List Support Tickets
**GET** `/support/tickets`
**Headers:** `Authorization: Bearer <token>`

---

## Promo Code Endpoints

### Validate Promo Code
**POST** `/promo-codes/validate`
**Headers:** `Authorization: Bearer <token>`
\`\`\`json
{
  "code": "SAVE20"
}
\`\`\`

**Response:**
\`\`\`json
{
  "message": "Promo code is valid",
  "discount_type": "percentage|fixed",
  "discount_value": 20.00
}
\`\`\`

---

## Error Responses

### 400 Bad Request
\`\`\`json
{
  "error": "Missing required fields"
}
\`\`\`

### 401 Unauthorized
\`\`\`json
{
  "error": "Token is missing or invalid"
}
\`\`\`

### 403 Forbidden
\`\`\`json
{
  "error": "Admin access required"
}
\`\`\`

### 404 Not Found
\`\`\`json
{
  "error": "Resource not found"
}
\`\`\`

### 409 Conflict
\`\`\`json
{
  "error": "Resource already exists"
}
\`\`\`

### 500 Internal Server Error
\`\`\`json
{
  "error": "Internal server error"
}
\`\`\`

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 500 | Internal Server Error |

---

## Order Statuses

- `pending` - Order created, awaiting courier assignment
- `assigned` - Courier assigned to order
- `picked_up` - Package picked up by courier
- `in_transit` - Package in transit to delivery address
- `delivered` - Package delivered successfully
- `cancelled` - Order cancelled

---

## User Roles

- `customer` - Can create and track orders
- `courier` - Can accept and deliver orders
- `admin` - Full platform access and management
