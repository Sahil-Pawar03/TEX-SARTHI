#!/usr/bin/env python3
"""
TEX-SARTHI Flask Backend Server
Run this file to start the Flask development server
"""

import os
from app import app, db
from models import User, Order, Customer, InventoryItem, Invoice, Delivery, Settings

def create_tables():
    """Create database tables"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully")
        
        # Create default admin user if not exists
        try:
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
        except Exception as e:
            print(f"Could not create admin user: {e}")
        
        # Create default settings if not exists
        try:
            default_settings = {
                'company_name': 'TEX-SARTHI',
                'company_address': 'Your Business Address',
                'company_phone': '+91-XXXXXXXXXX',
                'company_email': 'info@texsarthi.com',
                'company_gst': 'XXXXXXXXXXXXXXX',
                'tax_rate': '18',
                'currency': 'INR',
                'invoice_prefix': 'INV',
                'order_prefix': 'ORD',
                'delivery_prefix': 'DEL',
                'low_stock_threshold': '10',
                'auto_generate_invoice': 'true',
                'auto_generate_delivery': 'false',
                'backup_frequency': 'daily',
                'email_notifications': 'true',
                'sms_notifications': 'false'
            }
            
            for key, value in default_settings.items():
                setting = Settings.query.filter_by(key=key).first()
                if not setting:
                    setting = Settings(
                        key=key,
                        value=value,
                        description=f'Default setting for {key}'
                    )
                    db.session.add(setting)
            
            db.session.commit()
            print("Default settings created successfully")
        except Exception as e:
            print(f"Could not create default settings: {e}")

if __name__ == '__main__':
    # Create tables and default data
    create_tables()
    
    # Get configuration from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 3000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    print(f"Starting TEX-SARTHI Backend Server...")
    print(f"Server running on: http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"API Documentation: http://{host}:{port}/api/health")
    print("=" * 50)
    
    # Run the Flask app
    app.run(host=host, port=port, debug=debug)
