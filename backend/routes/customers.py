from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Customer, Order, db
from sqlalchemy import func

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    try:
        # Get query parameters
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Customer.query
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Customer.name.ilike(search_term),
                    Customer.email.ilike(search_term),
                    Customer.phone.ilike(search_term),
                    Customer.city.ilike(search_term)
                )
            )
        
        # Order by name
        query = query.order_by(Customer.name)
        
        # Paginate results
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        customers = pagination.items
        
        return jsonify({
            'customers': [customer.to_dict() for customer in customers],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch customers'}), 500

@customers_bp.route('/customers/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify({
            'customer': customer.to_dict(),
            'message': 'Customer retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch customer'}), 500

@customers_bp.route('/customers', methods=['POST'])
@jwt_required()
def create_customer():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        # Check if customer with same email already exists
        if data.get('email'):
            existing_customer = Customer.query.filter_by(email=data['email']).first()
            if existing_customer:
                return jsonify({'error': 'Customer with this email already exists'}), 409
        
        # Create new customer
        customer = Customer(
            name=data['name'],
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            pincode=data.get('pincode', ''),
            gst_number=data.get('gst_number', '')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'customer': customer.to_dict(),
            'message': 'Customer created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create customer'}), 500

@customers_bp.route('/customers/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'name' in data:
            customer.name = data['name']
        
        if 'email' in data:
            # Check if email is already taken by another customer
            if data['email']:
                existing_customer = Customer.query.filter_by(email=data['email']).first()
                if existing_customer and existing_customer.id != customer.id:
                    return jsonify({'error': 'Email already in use'}), 409
            customer.email = data['email']
        
        if 'phone' in data:
            customer.phone = data['phone']
        
        if 'address' in data:
            customer.address = data['address']
        
        if 'city' in data:
            customer.city = data['city']
        
        if 'state' in data:
            customer.state = data['state']
        
        if 'pincode' in data:
            customer.pincode = data['pincode']
        
        if 'gst_number' in data:
            customer.gst_number = data['gst_number']
        
        db.session.commit()
        
        return jsonify({
            'customer': customer.to_dict(),
            'message': 'Customer updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update customer'}), 500

@customers_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Check if customer has orders
        if customer.orders:
            return jsonify({'error': 'Cannot delete customer with existing orders'}), 400
        
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({'message': 'Customer deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete customer'}), 500

@customers_bp.route('/customers/<int:customer_id>/orders', methods=['GET'])
@jwt_required()
def get_customer_orders(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Get query parameters
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Order.query.filter_by(customer_id=customer_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        # Order by creation date (newest first)
        query = query.order_by(Order.created_at.desc())
        
        # Paginate results
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        orders = pagination.items
        
        return jsonify({
            'customer': customer.to_dict(),
            'orders': [order.to_dict() for order in orders],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch customer orders'}), 500

@customers_bp.route('/customers/<int:customer_id>/stats', methods=['GET'])
@jwt_required()
def get_customer_stats(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Get customer statistics
        total_orders = Order.query.filter_by(customer_id=customer_id).count()
        completed_orders = Order.query.filter_by(customer_id=customer_id, status='completed').count()
        pending_orders = Order.query.filter_by(customer_id=customer_id, status='pending').count()
        in_progress_orders = Order.query.filter_by(customer_id=customer_id, status='in_progress').count()
        
        # Get total spent
        total_spent = db.session.query(func.sum(Order.order_value)).filter(
            Order.customer_id == customer_id,
            Order.status == 'completed'
        ).scalar() or 0
        
        # Get outstanding amount
        outstanding_amount = db.session.query(func.sum(Order.order_value)).filter(
            Order.customer_id == customer_id,
            Order.status.in_(['pending', 'in_progress'])
        ).scalar() or 0
        
        # Get average order value
        avg_order_value = db.session.query(func.avg(Order.order_value)).filter(
            Order.customer_id == customer_id,
            Order.status == 'completed'
        ).scalar() or 0
        
        # Get last order date
        last_order = Order.query.filter_by(customer_id=customer_id).order_by(
            Order.created_at.desc()
        ).first()
        
        return jsonify({
            'customer': customer.to_dict(),
            'stats': {
                'totalOrders': total_orders,
                'completedOrders': completed_orders,
                'pendingOrders': pending_orders,
                'inProgressOrders': in_progress_orders,
                'totalSpent': float(total_spent),
                'outstandingAmount': float(outstanding_amount),
                'averageOrderValue': float(avg_order_value),
                'lastOrderDate': last_order.created_at.isoformat() if last_order else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch customer stats'}), 500

@customers_bp.route('/customers/search', methods=['GET'])
@jwt_required()
def search_customers():
    try:
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return jsonify({'customers': []}), 200
        
        # Search customers by name, email, or phone
        search_pattern = f"%{search_term}%"
        customers = Customer.query.filter(
            db.or_(
                Customer.name.ilike(search_pattern),
                Customer.email.ilike(search_pattern),
                Customer.phone.ilike(search_pattern)
            )
        ).limit(10).all()
        
        return jsonify({
            'customers': [customer.to_dict() for customer in customers]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to search customers'}), 500
