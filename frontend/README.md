# TEX-SARTHI Textile Management System

A comprehensive textile management system with both frontend and backend components for managing orders, inventory, customers, invoices, and deliveries.

## Features

### Frontend
- **Dashboard**: Overview of key metrics and quick actions
- **Order Management**: Create, view, edit, and track orders
- **Customer Management**: Manage customer information and relationships
- **Inventory Management**: Track stock levels and manage inventory items
- **Invoice Management**: Generate and manage invoices
- **Delivery Management**: Schedule and track deliveries
- **Reports & Analytics**: View business reports and analytics
- **Settings**: Configure business settings and preferences
- **Authentication**: Secure login and signup system

### Backend
- **RESTful API**: Complete API for all frontend operations
- **SQLite Database**: Lightweight, file-based database
- **JWT Authentication**: Secure token-based authentication
- **Data Validation**: Input validation and error handling
- **Rate Limiting**: API rate limiting for security
- **CORS Support**: Cross-origin resource sharing enabled

## Technology Stack

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript
- Local Storage (for offline functionality)

### Backend
- Node.js
- Express.js
- SQLite3
- JWT (JSON Web Tokens)
- bcryptjs (password hashing)
- CORS middleware
- Helmet (security headers)
- Express Rate Limit

## Installation & Setup

### Prerequisites
- Node.js (v14 or higher)
- npm (Node Package Manager)

### Backend Setup

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Initialize Database**
   ```bash
   npm run init-db
   ```
   This will create the SQLite database with all necessary tables and sample data.

3. **Start the Server**
   ```bash
   # Development mode (with auto-restart)
   npm run dev
   
   # Production mode
   npm start
   ```

   The server will start on `http://localhost:3000`

### Frontend Setup

The frontend is static HTML/CSS/JavaScript and can be served directly by the backend server or any web server.

1. **Using the Backend Server**
   - The backend serves static files from the current directory
   - Access the application at `http://localhost:3000`

2. **Using a Local Web Server**
   - You can use any static file server
   - For example, with Python: `python -m http.server 8000`
   - For example, with Node.js: `npx serve .`

## Default Login Credentials

After running the database initialization, you can log in with:

- **Email**: admin@texsarthi.com
- **Password**: admin123

Or create a new account using the signup page.

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/signup` - User registration

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

### Orders
- `GET /api/orders` - Get all orders (with optional filtering)
- `POST /api/orders` - Create new order
- `PUT /api/orders/:id` - Update order
- `DELETE /api/orders/:id` - Delete order

### Customers
- `GET /api/customers` - Get all customers (with optional search)
- `POST /api/customers` - Create new customer
- `PUT /api/customers/:id` - Update customer

### Inventory
- `GET /api/inventory` - Get all inventory items (with optional filtering)
- `POST /api/inventory` - Create new inventory item
- `PUT /api/inventory/:id` - Update inventory item

### Invoices
- `GET /api/invoices` - Get all invoices (with optional filtering)
- `POST /api/invoices` - Create new invoice

### Deliveries
- `GET /api/deliveries` - Get all deliveries (with optional filtering)
- `POST /api/deliveries` - Create new delivery

### Reports
- `GET /api/reports/sales` - Get sales report data

### Settings
- `GET /api/settings` - Get business settings
- `PUT /api/settings` - Update business settings

## Database Schema

### Tables
- **users**: User accounts and authentication
- **customers**: Customer information and statistics
- **inventory**: Inventory items and stock levels
- **orders**: Order management and tracking
- **invoices**: Invoice generation and payment tracking
- **deliveries**: Delivery scheduling and tracking
- **settings**: Business configuration

## File Structure

```
tex-sarthi/
├── frontend/
│   ├── index.html          # Dashboard page
│   ├── orders.html         # Orders management
│   ├── customers.html      # Customer management
│   ├── inventory.html      # Inventory management
│   ├── invoices.html       # Invoice management
│   ├── deliveries.html     # Delivery management
│   ├── reports.html        # Reports and analytics
│   ├── settings.html       # Settings page
│   ├── add-order.html      # Add new order form
│   ├── login.html          # Login page
│   ├── signup.html         # Signup page
│   ├── styles.css          # Main stylesheet
│   ├── auth.js             # Authentication utilities
│   └── api.js              # API integration
├── scripts/
│   └── init-database.js    # Database initialization script
├── server.js               # Main backend server
├── package.json            # Node.js dependencies
├── database.sqlite         # SQLite database (created after init)
└── README.md               # This file
```

## Development

### Adding New Features

1. **Backend**: Add new routes in `server.js`
2. **Frontend**: Update HTML pages and add JavaScript functionality in `api.js`
3. **Database**: Modify `scripts/init-database.js` for schema changes

### Environment Variables

You can set the following environment variables:

- `PORT`: Server port (default: 3000)
- `JWT_SECRET`: Secret key for JWT tokens (default: 'tex-sarthi-secret-key-2024')
- `NODE_ENV`: Environment mode (development/production)

## Security Features

- Password hashing with bcryptjs
- JWT token authentication
- Rate limiting on API endpoints
- CORS protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection headers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.

## Changelog

### Version 1.0.0
- Initial release
- Complete frontend and backend implementation
- All core features implemented
- Database initialization and sample data
- Authentication system
- API integration
