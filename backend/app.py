from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tex_sarthi.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string-change-this')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize database first
from models import db, User, Order, Customer, InventoryItem, Invoice, Delivery, Settings
db.init_app(app)

# Initialize other extensions
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)

# Import routes
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.orders import orders_bp
from routes.customers import customers_bp
from routes.inventory import inventory_bp
from routes.invoices import invoices_bp
from routes.deliveries import deliveries_bp
from routes.reports import reports_bp
from routes.settings import settings_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(customers_bp, url_prefix='/api')
app.register_blueprint(inventory_bp, url_prefix='/api')
app.register_blueprint(invoices_bp, url_prefix='/api')
app.register_blueprint(deliveries_bp, url_prefix='/api')
app.register_blueprint(reports_bp, url_prefix='/api')
app.register_blueprint(settings_bp, url_prefix='/api')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# Initialize database
def create_tables():
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin_user = User.query.filter_by(email='admin@texsarthi.com').first()
        if not admin_user:
            admin_user = User(
                name='Admin User',
                email='admin@texsarthi.com',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: admin@texsarthi.com / admin123")

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=3000)
