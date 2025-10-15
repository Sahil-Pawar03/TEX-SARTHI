# TEX-SARTHI

A comprehensive textile business management system with order tracking, inventory management, customer relationship management, and delivery tracking.

## 🚀 Quick Start

### Option 1: Auto Start (Recommended)
Double-click `start-app.bat` to automatically start both backend and frontend servers.

### Option 2: Manual Start

1. **Start Backend Server:**
   ```bash
   cd backend
   venv\Scripts\activate
   python run.py
   ```

2. **Start Frontend Server:**
   ```bash
   cd frontend
   python serve.py
   ```

### Access the Application
- **Frontend Web App:** http://localhost:8080
- **Backend API:** http://localhost:3000
- **API Health Check:** http://localhost:3000/api/health

## 👤 Default Login Credentials
- **Email:** admin@texsarthi.com
- **Password:** admin123

## 📁 Project Structure

```
TEX-SARTHI/
├── backend/                 # Flask API Server
│   ├── routes/             # API endpoints
│   │   ├── auth.py         # Authentication routes
│   │   ├── orders.py       # Order management
│   │   ├── customers.py    # Customer management
│   │   ├── inventory.py    # Inventory management
│   │   ├── invoices.py     # Invoice management
│   │   ├── deliveries.py   # Delivery tracking
│   │   ├── dashboard.py    # Dashboard statistics
│   │   ├── reports.py      # Report generation
│   │   └── settings.py     # Application settings
│   ├── models.py           # Database models
│   ├── app.py             # Main Flask application
│   ├── run.py             # Server startup script
│   └── requirements.txt    # Python dependencies
├── frontend/               # Web Interface
│   ├── *.html             # Web pages
│   ├── styles.css         # Styling
│   ├── api.js             # API integration
│   ├── auth.js            # Authentication handling
│   └── serve.py           # Frontend development server
├── start-app.bat          # Auto-start script
└── README.md              # This file
```

## 🎯 Features

### Core Modules
- **📊 Dashboard** - Real-time business statistics and quick actions
- **📦 Order Management** - Complete order lifecycle tracking
- **👥 Customer Management** - Customer database with history
- **📄 Invoice Management** - Automated invoice generation
- **🚛 Delivery Tracking** - Delivery scheduling and status updates
- **📦 Inventory Management** - Stock tracking with low-stock alerts
- **📈 Reports & Analytics** - Business intelligence and reporting
- **⚙️ Settings** - Configurable business parameters

### Technical Features
- **Authentication** - JWT-based secure authentication
- **RESTful API** - Complete REST API for all operations
- **Real-time Updates** - Live dashboard statistics
- **Responsive Design** - Mobile-friendly interface
- **Data Export** - Export capabilities for reports
- **CORS Support** - Cross-origin resource sharing enabled

## 🛠️ Technology Stack

### Backend
- **Framework:** Flask 2.3.3
- **Database:** SQLite (default), PostgreSQL (production)
- **Authentication:** JWT (Flask-JWT-Extended)
- **ORM:** SQLAlchemy
- **API:** RESTful with JSON responses

### Frontend
- **Technology:** Vanilla JavaScript, HTML5, CSS3
- **Design:** Responsive, Mobile-first
- **API Integration:** Fetch API with authentication
- **UI Components:** Custom CSS framework

## 📊 Database Schema

### Core Models
- **Users** - Authentication and user management
- **Customers** - Customer information and statistics
- **Orders** - Order details with status tracking
- **Inventory** - Stock management with alerts
- **Invoices** - Invoice generation and payment tracking
- **Deliveries** - Delivery scheduling and tracking
- **Settings** - Application configuration

## 🔧 Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git (optional)

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend Setup
```bash
cd frontend
python serve.py
```

## 📡 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/signup` - User registration
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update user profile

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/charts/sales` - Sales chart data
- `GET /api/dashboard/charts/orders` - Orders chart data

### Orders
- `GET /api/orders` - List all orders
- `POST /api/orders` - Create new order
- `GET /api/orders/{id}` - Get specific order
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order

### Customers
- `GET /api/customers` - List all customers
- `POST /api/customers` - Create new customer
- `GET /api/customers/{id}` - Get specific customer
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

### Inventory
- `GET /api/inventory` - List inventory items
- `POST /api/inventory` - Create inventory item
- `PUT /api/inventory/{id}` - Update inventory item
- `DELETE /api/inventory/{id}` - Delete inventory item

### And more...
See [backend/README.md](backend/README.md) for complete API documentation.

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Input validation and sanitization
- SQL injection protection via SQLAlchemy ORM
- XSS prevention

## 🚀 Production Deployment

### Backend (Using Gunicorn)
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:3000 app:app
```

### Environment Variables
Create a `.env` file in the backend directory:
```env
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=postgresql://user:password@localhost/texsarthi
FLASK_ENV=production
```

### Frontend (Static Hosting)
The frontend can be deployed to any static hosting service like:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront

## 📝 Usage Examples

### Creating an Order
1. Navigate to **Orders** → **Add New Order**
2. Select or create a customer
3. Fill in order details (type, fabric, measurements, etc.)
4. Set delivery date and payment terms
5. Save the order

### Managing Inventory
1. Go to **Inventory**
2. Add new items with stock levels
3. Set minimum stock thresholds
4. Monitor low-stock alerts on dashboard

### Generating Reports
1. Visit **Reports** section
2. Select report type (Sales, Inventory, Financial)
3. Set date range filters
4. Generate and export reports

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the documentation
2. Review error logs
3. Contact the development team

## 📄 License

This project is proprietary software for TEX-SARTHI business operations.

---

**TEX-SARTHI** - Streamlining textile business operations with modern technology.
