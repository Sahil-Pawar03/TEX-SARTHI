#!/usr/bin/env python3
"""
Database initialization script for TEX-SARTHI Backend
Run this to initialize the database with sample data
"""

from app import app, db
from models import User, Customer, InventoryItem, Order, Invoice, Delivery, Settings
from datetime import datetime, date, timedelta
import uuid

def generate_order_number():
    """Generate unique order number"""
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

def generate_invoice_number():
    """Generate unique invoice number"""
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

def generate_delivery_number():
    """Generate unique delivery number"""
    return f"DEL-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        # Drop all tables and recreate
        print("Dropping existing tables...")
        db.drop_all()
        print("Creating new tables...")
        db.create_all()
        
        # Create admin user
        print("Creating admin user...")
        admin_user = User(
            name='Admin User',
            email='admin@texsarthi.com',
            role='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Create regular user
        regular_user = User(
            name='John Doe',
            email='john@texsarthi.com',
            role='user'
        )
        regular_user.set_password('password123')
        db.session.add(regular_user)
        
        # Create default settings
        print("Creating default settings...")
        default_settings = {
            'company_name': 'TEX-SARTHI',
            'company_address': '123 Business Street, City, State 12345',
            'company_phone': '+91-9876543210',
            'company_email': 'info@texsarthi.com',
            'company_gst': '29ABCDE1234F1Z5',
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
            setting = Settings(
                key=key,
                value=value,
                description=f'Default setting for {key}'
            )
            db.session.add(setting)
        
        # Create sample customers
        print("Creating sample customers...")
        customers_data = [
            {
                'name': 'Rajesh Kumar',
                'email': 'rajesh@email.com',
                'phone': '+91-9876543210',
                'address': '123 Main Street, Mumbai, Maharashtra',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'pincode': '400001',
                'gst_number': '27ABCDE1234F1Z5'
            },
            {
                'name': 'Priya Sharma',
                'email': 'priya@email.com',
                'phone': '+91-9876543211',
                'address': '456 Park Avenue, Delhi, Delhi',
                'city': 'Delhi',
                'state': 'Delhi',
                'pincode': '110001',
                'gst_number': '07ABCDE1234F1Z5'
            },
            {
                'name': 'Amit Patel',
                'email': 'amit@email.com',
                'phone': '+91-9876543212',
                'address': '789 Garden Road, Bangalore, Karnataka',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': '560001',
                'gst_number': '29ABCDE1234F1Z5'
            }
        ]
        
        customers = []
        for customer_data in customers_data:
            customer = Customer(**customer_data)
            db.session.add(customer)
            customers.append(customer)
        
        # Create sample inventory items
        print("Creating sample inventory items...")
        inventory_data = [
            {
                'item_name': 'Cotton Shirt Fabric',
                'type': 'fabric',
                'color': 'White',
                'current_stock': 100,
                'min_stock': 20,
                'cost_per_unit': 150.0,
                'supplier': 'Fabric Supplier Co.',
                'status': 'in_stock'
            },
            {
                'item_name': 'Denim Fabric',
                'type': 'fabric',
                'color': 'Blue',
                'current_stock': 50,
                'min_stock': 15,
                'cost_per_unit': 200.0,
                'supplier': 'Denim Mills Ltd.',
                'status': 'in_stock'
            },
            {
                'item_name': 'Silk Thread',
                'type': 'thread',
                'color': 'Black',
                'current_stock': 5,
                'min_stock': 10,
                'cost_per_unit': 25.0,
                'supplier': 'Thread Co.',
                'status': 'low_stock'
            },
            {
                'item_name': 'Plastic Buttons',
                'type': 'button',
                'color': 'White',
                'current_stock': 0,
                'min_stock': 50,
                'cost_per_unit': 2.0,
                'supplier': 'Button Supplier',
                'status': 'out_of_stock'
            }
        ]
        
        for item_data in inventory_data:
            item = InventoryItem(**item_data)
            db.session.add(item)
        
        # Create sample orders
        print("Creating sample orders...")
        orders_data = [
            {
                'order_number': generate_order_number(),
                'customer_id': 1,
                'customer_name': 'Rajesh Kumar',
                'order_type': 'shirt',
                'fabric': 'Cotton',
                'color': 'White',
                'quantity': 2,
                'order_value': 2000.0,
                'advance_payment': 500.0,
                'delivery_date': date.today() + timedelta(days=7),
                'status': 'in_progress',
                'notes': 'Regular fit, medium size'
            },
            {
                'order_number': generate_order_number(),
                'customer_id': 2,
                'customer_name': 'Priya Sharma',
                'order_type': 'suit',
                'fabric': 'Wool',
                'color': 'Black',
                'quantity': 1,
                'order_value': 5000.0,
                'advance_payment': 1000.0,
                'delivery_date': date.today() + timedelta(days=14),
                'status': 'pending',
                'notes': 'Formal suit for office'
            },
            {
                'order_number': generate_order_number(),
                'customer_id': 3,
                'customer_name': 'Amit Patel',
                'order_type': 'pant',
                'fabric': 'Denim',
                'color': 'Blue',
                'quantity': 3,
                'order_value': 3000.0,
                'advance_payment': 0.0,
                'delivery_date': date.today() + timedelta(days=10),
                'status': 'completed',
                'notes': 'Casual jeans'
            }
        ]
        
        orders = []
        for order_data in orders_data:
            order = Order(**order_data)
            db.session.add(order)
            orders.append(order)

        # Ensure primary keys are assigned before creating related rows
        db.session.flush()
        
        # Create sample invoices
        print("Creating sample invoices...")
        for i, order in enumerate(orders):
            if order.status == 'completed':
                invoice = Invoice(
                    invoice_number=generate_invoice_number(),
                    order_id=order.id,
                    customer_id=order.customer_id,
                    amount=order.order_value - order.advance_payment,
                    tax_amount=(order.order_value - order.advance_payment) * 0.18,
                    total_amount=(order.order_value - order.advance_payment) * 1.18,
                    status='paid',
                    due_date=date.today() - timedelta(days=5),
                    paid_date=date.today() - timedelta(days=3),
                    payment_method='Cash',
                    notes='Payment received'
                )
                db.session.add(invoice)
            elif order.status == 'in_progress':
                invoice = Invoice(
                    invoice_number=generate_invoice_number(),
                    order_id=order.id,
                    customer_id=order.customer_id,
                    amount=order.order_value - order.advance_payment,
                    tax_amount=(order.order_value - order.advance_payment) * 0.18,
                    total_amount=(order.order_value - order.advance_payment) * 1.18,
                    status='pending',
                    due_date=date.today() + timedelta(days=7),
                    notes='Payment pending'
                )
                db.session.add(invoice)
        
        # Create sample deliveries
        print("Creating sample deliveries...")
        for order in orders:
            if order.status in ['completed', 'in_progress']:
                delivery = Delivery(
                    delivery_number=generate_delivery_number(),
                    order_id=order.id,
                    customer_id=order.customer_id,
                    delivery_date=order.delivery_date,
                    delivery_address=order.customer.address if order.customer else 'Customer Address',
                    status='delivered' if order.status == 'completed' else 'scheduled',
                    delivery_person='Delivery Person',
                    tracking_number=f'TRK{(order.id or 0):06d}',
                    notes='Handle with care'
                )
                db.session.add(delivery)
        
        # Commit all changes
        print("Committing changes to database...")
        db.session.commit()
        
        print("=" * 50)
        print("✅ Database initialized successfully!")
        print("=" * 50)
        print("Sample data created:")
        print(f"- Users: {User.query.count()}")
        print(f"- Customers: {Customer.query.count()}")
        print(f"- Inventory Items: {InventoryItem.query.count()}")
        print(f"- Orders: {Order.query.count()}")
        print(f"- Invoices: {Invoice.query.count()}")
        print(f"- Deliveries: {Delivery.query.count()}")
        print(f"- Settings: {Settings.query.count()}")
        print("=" * 50)
        print("Default login credentials:")
        print("Email: admin@texsarthi.com")
        print("Password: admin123")
        print("=" * 50)

if __name__ == "__main__":
    init_database()
