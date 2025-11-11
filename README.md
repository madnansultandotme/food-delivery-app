# Courier Delivery App - Flask API

A production-ready Flask API for a courier delivery application with authentication, order management, real-time tracking, ratings, payments, and admin features.

## Features

✅ **Authentication**
- User registration and login
- JWT token-based authentication
- Role-based access control (Customer, Courier, Admin)

✅ **Order Management**
- Create and manage delivery orders
- Order status tracking (pending → delivered)
- Order assignment to couriers
- Real-time location tracking

✅ **User Management**
- User profiles and information
- Profile updates
- User verification system

✅ **Ratings & Reviews**
- Rate deliveries and users
- Average rating calculation
- Review history

✅ **Payment Processing**
- Multiple payment methods support
- Payment tracking and history
- Transaction management

✅ **Admin Dashboard**
- User management
- Order monitoring
- Platform statistics
- Revenue tracking

✅ **Support System**
- Support ticket creation
- Ticket management
- Priority-based support

✅ **Promotional Codes**
- Promo code validation
- Discount application
- Usage tracking

## Technology Stack

- **Framework:** Flask
- **Database:** PostgreSQL (Supabase)
- **Authentication:** JWT
- **Hosting:** Vercel Serverless Functions
- **Password Security:** bcrypt

## Local Development

\`\`\`bash
# Clone repository
git clone <repo-url>
cd courier-delivery-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run application
python api/index.py
\`\`\`

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

## API Documentation

Complete API documentation available in [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

### Quick Start

1. **Register User**
   \`\`\`bash
   curl -X POST http://localhost:5000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "name": "John Doe",
       "email": "john@example.com",
       "phone": "+1234567890",
       "password": "password123",
       "role": "customer"
     }'
   \`\`\`

2. **Login**
   \`\`\`bash
   curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "email": "john@example.com",
       "password": "password123"
     }'
   \`\`\`

3. **Create Order**
   \`\`\`bash
   curl -X POST http://localhost:5000/api/orders \
     -H "Authorization: Bearer <your-token>" \
     -H "Content-Type: application/json" \
     -d '{
       "pickup_address": "123 Main St",
       "delivery_address": "456 Oak Ave",
       "package_description": "Documents"
     }'
   \`\`\`

## Project Structure

\`\`\`
├── api/
│   └── index.py              # Main Flask application
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel configuration
├── package.json             # Project metadata
├── API_DOCUMENTATION.md     # API documentation
├── DEPLOYMENT.md            # Deployment guide
└── README.md                # This file
\`\`\`

## Database Schema

### Users
- Basic user information
- Authentication credentials
- Location data
- Verification status

### Orders
- Order details and tracking
- Customer and courier information
- Pickup and delivery locations
- Payment and status tracking

### Order Status History
- Real-time location updates
- Status change history
- Delivery timeline

### Ratings
- User ratings and reviews
- Review history

### Payments
- Payment records
- Transaction information
- Payment status

### Support Tickets
- User support requests
- Ticket prioritization
- Issue tracking

### Promo Codes
- Discount codes
- Usage tracking
- Validity periods

## Error Handling

All errors follow a standard response format:
\`\`\`json
{
  "error": "Error description"
}
\`\`\`

## Security Features

✅ Password hashing with bcrypt
✅ JWT token authentication
✅ CORS enabled
✅ Role-based access control
✅ SQL injection prevention
✅ Secure environment variable management

## Performance

- Connection pooling support
- Efficient database queries
- Pagination for list endpoints
- Real-time tracking capabilities

## Future Enhancements

- [ ] WebSocket support for real-time notifications
- [ ] Geofencing for delivery zones
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app push notifications
- [ ] Advanced search and filtering
- [ ] Invoice generation
- [ ] Recurring deliveries

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please create a support ticket through the API or contact support@courierdelvery.app

---

Built with ❤️ for efficient courier delivery management
