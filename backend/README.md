# TEX-SARTHI Backend API

A comprehensive Flask-based REST API for managing textile business operations including orders, customers, inventory, invoices, and deliveries.

## Features

- **Authentication & Authorization**: JWT-based authentication with user management
- **Order Management**: Complete CRUD operations for orders with status tracking
- **Customer Management**: Customer database with order history and statistics
- **Inventory Management**: Stock tracking with low-stock alerts
- **Invoice Management**: Automated invoice generation with tax calculations
- **Delivery Management**: Delivery scheduling and tracking
- **Reports & Analytics**: Sales, inventory, customer, and financial reports
- **Settings Management**: Configurable business settings

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/signup` - User registration
- `POST /api/logout` - User logout
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update user profile

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/charts/sales` - Get sales chart data
- `GET /api/dashboard/charts/orders` - Get orders chart data

### Orders
- `GET /api/orders` - Get all orders (with filtering)
- `POST /api/orders` - Create new order
- `GET /api/orders/{id}` - Get specific order
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order
- `PUT /api/orders/{id}/status` - Update order status
- `POST /api/orders/{id}/invoice` - Create invoice for order

### Customers
- `GET /api/customers` - Get all customers
- `POST /api/customers` - Create new customer
- `GET /api/customers/{id}` - Get specific customer
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer
- `GET /api/customers/{id}/orders` - Get customer orders
- `GET /api/customers/{id}/stats` - Get customer statistics
- `GET /api/customers/search` - Search customers

### Inventory
- `GET /api/inventory` - Get all inventory items
- `POST /api/inventory` - Create new inventory item
- `GET /api/inventory/{id}` - Get specific inventory item
- `PUT /api/inventory/{id}` - Update inventory item
- `DELETE /api/inventory/{id}` - Delete inventory item
- `PUT /api/inventory/{id}/stock` - Update stock levels
- `GET /api/inventory/stats` - Get inventory statistics
- `GET /api/inventory/types` - Get inventory types

### Invoices
- `GET /api/invoices` - Get all invoices
- `POST /api/invoices` - Create new invoice
- `GET /api/invoices/{id}` - Get specific invoice
- `PUT /api/invoices/{id}` - Update invoice
- `DELETE /api/invoices/{id}` - Delete invoice
- `PUT /api/invoices/{id}/pay` - Mark invoice as paid
- `GET /api/invoices/stats` - Get invoice statistics

### Deliveries
- `GET /api/deliveries` - Get all deliveries
- `POST /api/deliveries` - Create new delivery
- `GET /api/deliveries/{id}` - Get specific delivery
- `PUT /api/deliveries/{id}` - Update delivery
- `DELETE /api/deliveries/{id}` - Delete delivery
- `PUT /api/deliveries/{id}/status` - Update delivery status
- `GET /api/deliveries/stats` - Get delivery statistics
- `GET /api/deliveries/today` - Get today's deliveries

### Reports
- `GET /api/reports/sales` - Generate sales report
- `GET /api/reports/inventory` - Generate inventory report
- `GET /api/reports/customers` - Generate customers report
- `GET /api/reports/financial` - Generate financial report

### Settings
- `GET /api/settings` - Get all settings
- `PUT /api/settings` - Update settings
- `GET /api/settings/{key}` - Get specific setting
- `PUT /api/settings/{key}` - Update specific setting
- `DELETE /api/settings/{key}` - Delete setting
- `POST /api/settings/reset` - Reset to defaults
- `POST /api/settings/backup` - Backup settings
- `POST /api/settings/restore` - Restore settings

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TEX-SARTHI/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file with your configuration
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   DATABASE_URL=sqlite:///tex_sarthi.db
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

## Database Setup

The application uses SQLAlchemy with support for:
- **SQLite** (default for development)
- **PostgreSQL** (recommended for production)
- **MySQL** (alternative for production)

### Database Models

- **User**: User authentication and profile
- **Customer**: Customer information and statistics
- **Order**: Order details and status tracking
- **InventoryItem**: Stock management and tracking
- **Invoice**: Invoice generation and payment tracking
- **Delivery**: Delivery scheduling and tracking
- **Settings**: Application configuration

## Configuration

### Environment Variables

- `SECRET_KEY`: Flask secret key for session management
- `JWT_SECRET_KEY`: JWT token signing key
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Environment (development/production)
- `FLASK_DEBUG`: Debug mode (True/False)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

### Default Settings

The application comes with default business settings that can be customized:
- Company information
- Tax rates
- Invoice/Order prefixes
- Stock thresholds
- Notification preferences

## API Authentication

All API endpoints (except login/signup) require JWT authentication:

```bash
# Login to get token
curl -X POST http://localhost:3000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@texsarthi.com", "password": "admin123"}'

# Use token in subsequent requests
curl -X GET http://localhost:3000/api/orders \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Error Handling

The API returns consistent error responses:

```json
{
  "error": "Error message",
  "code": 400
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `409`: Conflict
- `500`: Internal Server Error

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python run.py
```

### Database Migrations

For production deployments, consider using Flask-Migrate:

```bash
pip install Flask-Migrate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Testing

```bash
# Run tests (when implemented)
python -m pytest tests/
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:3000 app:app
```

### Using Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 3000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "app:app"]
```

## Security Considerations

- Change default admin credentials
- Use strong secret keys in production
- Enable HTTPS in production
- Implement rate limiting
- Regular security updates
- Database backup strategy

## Support

For issues and questions:
1. Check the API documentation
2. Review error logs
3. Contact the development team

## License

This project is proprietary software for TEX-SARTHI business operations.
