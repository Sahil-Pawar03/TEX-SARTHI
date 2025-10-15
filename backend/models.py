from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    gst_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def to_dict(self):
        # Calculate customer statistics
        total_orders = len(self.orders)
        total_spent = sum(order.order_value for order in self.orders if order.status == 'completed')
        outstanding_amount = sum(order.order_value for order in self.orders if order.status in ['pending', 'in_progress'])
        last_order_date = max([order.created_at for order in self.orders]) if self.orders else None
        
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'gst_number': self.gst_number,
            'total_orders': total_orders,
            'total_spent': total_spent,
            'outstanding_amount': outstanding_amount,
            'last_order_date': last_order_date.isoformat() if last_order_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # fabric, thread, button, etc.
    color = db.Column(db.String(50))
    current_stock = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=0)
    cost_per_unit = db.Column(db.Float, default=0.0)
    supplier = db.Column(db.String(100))
    status = db.Column(db.String(20), default='in_stock')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def total_value(self):
        return self.current_stock * self.cost_per_unit
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'type': self.type,
            'color': self.color,
            'current_stock': self.current_stock,
            'min_stock': self.min_stock,
            'cost_per_unit': self.cost_per_unit,
            'total_value': self.total_value,
            'supplier': self.supplier,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)  # Denormalized for performance
    order_type = db.Column(db.String(50), nullable=False)  # shirt, pant, suit, etc.
    fabric = db.Column(db.String(100))
    color = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=1)
    measurements = db.Column(db.Text)  # JSON string for measurements
    order_value = db.Column(db.Float, nullable=False)
    advance_payment = db.Column(db.Float, default=0.0)
    delivery_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoices = db.relationship('Invoice', backref='order', lazy=True)
    deliveries = db.relationship('Delivery', backref='order', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'order_type': self.order_type,
            'fabric': self.fabric,
            'color': self.color,
            'quantity': self.quantity,
            'measurements': self.measurements,
            'order_value': self.order_value,
            'advance_payment': self.advance_payment,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    due_date = db.Column(db.Date)
    paid_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'amount': self.amount,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Delivery(db.Model):
    __tablename__ = 'deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    delivery_number = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_transit, delivered, failed
    delivery_person = db.Column(db.String(100))
    tracking_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'delivery_number': self.delivery_number,
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'delivery_address': self.delivery_address,
            'status': self.status,
            'delivery_person': self.delivery_person,
            'tracking_number': self.tracking_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
