"""
Sample Data Creator for TEX-SARTHI
Creates sample orders, customers, and inventory for testing AI invoice generation
"""

from flask import Flask
from models import db, Customer, Order, InventoryItem
from datetime import datetime, date, timedelta
import json

def create_sample_data():
    """Create sample data for testing"""
    
    # Create sample customers
    customers_data = [
        {
            'name': 'Rajesh Kumar',
            'email': 'rajesh@example.com',
            'phone': '+91-9876543210',
            'address': '123 MG Road',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400001',
            'gst_number': 'GST123456789'
        },
        {
            'name': 'Priya Textiles',
            'email': 'info@priyatextiles.com',
            'phone': '+91-9876543211',
            'address': '456 Commercial Street',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'pincode': '560001',
            'gst_number': 'GST987654321'
        },
        {
            'name': 'Mumbai Fabrics Ltd',
            'email': 'sales@mumbaifabrics.com',
            'phone': '+91-9876543212',
            'address': '789 Textile Market',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400002',
            'gst_number': 'GST456789123'
        },
        {
            'name': 'Silk Sarees Palace',
            'email': 'orders@silkpalace.com',
            'phone': '+91-9876543213',
            'address': '321 Silk Market',
            'city': 'Chennai',
            'state': 'Tamil Nadu',
            'pincode': '600001',
            'gst_number': 'GST321654987'
        }
    ]
    
    # Create customers
    created_customers = []
    for customer_data in customers_data:
        existing = Customer.query.filter_by(email=customer_data['email']).first()
        if not existing:
            customer = Customer(**customer_data)
            db.session.add(customer)
            created_customers.append(customer)
    
    db.session.commit()
    
    # Get all customers (including existing ones)
    all_customers = Customer.query.all()
    
    # Create sample orders with different complexities for AI testing
    orders_data = [
        {
            'customer_id': all_customers[0].id,
            'customer_name': all_customers[0].name,
            'order_type': 'shirt',
            'fabric': 'cotton',
            'color': 'white',
            'quantity': 2,
            'measurements': json.dumps({
                'chest': '40',
                'shoulder': '16',
                'length': '28',
                'sleeve': '24'
            }),
            'order_value': 2500.0,
            'advance_payment': 1000.0,
            'delivery_date': date.today() + timedelta(days=7),
            'status': 'in_progress',
            'notes': 'Premium cotton shirt with custom fit'
        },
        {
            'customer_id': all_customers[1].id,
            'customer_name': all_customers[1].name,
            'order_type': 'suit',
            'fabric': 'wool',
            'color': 'navy blue',
            'quantity': 1,
            'measurements': json.dumps({
                'chest': '42',
                'waist': '36',
                'length': '30',
                'inseam': '32'
            }),
            'order_value': 8500.0,
            'advance_payment': 4000.0,
            'delivery_date': date.today() + timedelta(days=14),
            'status': 'pending',
            'notes': 'Premium wool suit with complex tailoring and embroidery work'
        },
        {
            'customer_id': all_customers[2].id,
            'customer_name': all_customers[2].name,
            'order_type': 'dress',
            'fabric': 'silk',
            'color': 'maroon',
            'quantity': 1,
            'measurements': json.dumps({
                'bust': '36',
                'waist': '30',
                'hips': '38',
                'length': '42'
            }),
            'order_value': 4500.0,
            'advance_payment': 2000.0,
            'delivery_date': date.today() + timedelta(days=10),
            'status': 'pending',
            'notes': 'Silk dress with premium finishing'
        },
        {
            'customer_id': all_customers[3].id,
            'customer_name': all_customers[3].name,
            'order_type': 'saree',
            'fabric': 'silk',
            'color': 'red',
            'quantity': 1,
            'measurements': json.dumps({
                'blouse_size': '36',
                'length': '6_yards'
            }),
            'order_value': 6000.0,
            'advance_payment': 3000.0,
            'delivery_date': date.today() + timedelta(days=5),
            'status': 'pending',
            'notes': 'Traditional silk saree with blouse stitching and embroidery'
        },
        {
            'customer_id': all_customers[0].id,
            'customer_name': all_customers[0].name,
            'order_type': 'pant',
            'fabric': 'denim',
            'color': 'blue',
            'quantity': 3,
            'measurements': json.dumps({
                'waist': '32',
                'inseam': '30',
                'length': '42'
            }),
            'order_value': 1800.0,
            'advance_payment': 500.0,
            'delivery_date': date.today() + timedelta(days=3),
            'status': 'pending',
            'notes': 'Alteration services for existing pants'
        }
    ]
    
    # Generate unique order numbers
    from datetime import datetime
    import uuid
    
    created_orders = []
    for order_data in orders_data:
        # Generate unique order number
        order_data['order_number'] = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        order = Order(**order_data)
        db.session.add(order)
        created_orders.append(order)
    
    db.session.commit()
    
    # Create sample inventory items
    inventory_data = [
        {
            'item_name': 'Premium Cotton Fabric',
            'type': 'fabric',
            'color': 'white',
            'current_stock': 50,
            'min_stock': 10,
            'cost_per_unit': 150.0,
            'supplier': 'Cotton Mills Ltd',
            'status': 'in_stock'
        },
        {
            'item_name': 'Silk Fabric',
            'type': 'fabric',
            'color': 'various',
            'current_stock': 25,
            'min_stock': 5,
            'cost_per_unit': 800.0,
            'supplier': 'Silk Traders',
            'status': 'in_stock'
        },
        {
            'item_name': 'Wool Fabric',
            'type': 'fabric',
            'color': 'navy',
            'current_stock': 8,
            'min_stock': 10,
            'cost_per_unit': 1200.0,
            'supplier': 'Premium Textiles',
            'status': 'low_stock'
        },
        {
            'item_name': 'Embroidery Thread',
            'type': 'thread',
            'color': 'gold',
            'current_stock': 100,
            'min_stock': 20,
            'cost_per_unit': 25.0,
            'supplier': 'Thread Suppliers',
            'status': 'in_stock'
        }
    ]
    
    created_inventory = []
    for item_data in inventory_data:
        existing = InventoryItem.query.filter_by(
            item_name=item_data['item_name'], 
            type=item_data['type']
        ).first()
        if not existing:
            item = InventoryItem(**item_data)
            db.session.add(item)
            created_inventory.append(item)
    
    db.session.commit()
    
    return {
        'customers_created': len(created_customers),
        'orders_created': len(created_orders),
        'inventory_created': len(created_inventory),
        'order_ids': [order.id for order in created_orders]
    }

if __name__ == "__main__":
    # This script can be run independently to create sample data
    from app import app
    
    with app.app_context():
        result = create_sample_data()
        print("Sample Data Creation Results:")
        print("=" * 40)
        print(f"Customers created: {result['customers_created']}")
        print(f"Orders created: {result['orders_created']}")
        print(f"Inventory items created: {result['inventory_created']}")
        print(f"Order IDs for AI testing: {result['order_ids']}")
        print("\nSample data created successfully!")
        print("You can now test AI invoice generation with these orders.")