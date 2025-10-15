from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Order, Customer, db
from datetime import datetime, date
import uuid

orders_bp = Blueprint('orders', __name__)

def generate_order_number():
    """Generate unique order number"""
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

@orders_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    try:
        # Get query parameters
        status = request.args.get('status')
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Order.query
        
        if status:
            query = query.filter(Order.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Order.order_number.ilike(search_term),
                    Order.customer_name.ilike(search_term),
                    Order.order_type.ilike(search_term),
                    Order.fabric.ilike(search_term)
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(Order.created_at.desc())
        
        # Paginate results
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        orders = pagination.items
        
        return jsonify({
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
        return jsonify({'error': 'Failed to fetch orders'}), 500

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({
            'order': order.to_dict(),
            'message': 'Order retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch order'}), 500

@orders_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['customer_id', 'customer_name', 'order_type', 'order_value']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Create new order
        order = Order(
            order_number=generate_order_number(),
            customer_id=data['customer_id'],
            customer_name=data['customer_name'],
            order_type=data['order_type'],
            fabric=data.get('fabric', ''),
            color=data.get('color', ''),
            quantity=data.get('quantity', 1),
            measurements=data.get('measurements', ''),
            order_value=float(data['order_value']),
            advance_payment=float(data.get('advance_payment', 0)),
            delivery_date=datetime.strptime(data['delivery_date'], '%Y-%m-%d').date() if data.get('delivery_date') else None,
            status=data.get('status', 'pending'),
            notes=data.get('notes', '')
        )
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify({
            'order': order.to_dict(),
            'message': 'Order created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create order'}), 500

@orders_bp.route('/orders/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'customer_id' in data:
            customer = Customer.query.get(data['customer_id'])
            if not customer:
                return jsonify({'error': 'Customer not found'}), 404
            order.customer_id = data['customer_id']
        
        if 'customer_name' in data:
            order.customer_name = data['customer_name']
        
        if 'order_type' in data:
            order.order_type = data['order_type']
        
        if 'fabric' in data:
            order.fabric = data['fabric']
        
        if 'color' in data:
            order.color = data['color']
        
        if 'quantity' in data:
            order.quantity = int(data['quantity'])
        
        if 'measurements' in data:
            order.measurements = data['measurements']
        
        if 'order_value' in data:
            order.order_value = float(data['order_value'])
        
        if 'advance_payment' in data:
            order.advance_payment = float(data['advance_payment'])
        
        if 'delivery_date' in data:
            if data['delivery_date']:
                order.delivery_date = datetime.strptime(data['delivery_date'], '%Y-%m-%d').date()
            else:
                order.delivery_date = None
        
        if 'status' in data:
            order.status = data['status']
        
        if 'notes' in data:
            order.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'order': order.to_dict(),
            'message': 'Order updated successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update order'}), 500

@orders_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check if order can be deleted (not completed or has invoices)
        if order.status == 'completed':
            return jsonify({'error': 'Cannot delete completed order'}), 400
        
        if order.invoices:
            return jsonify({'error': 'Cannot delete order with invoices'}), 400
        
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({'message': 'Order deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete order'}), 500

@orders_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        order.status = data['status']
        db.session.commit()
        
        return jsonify({
            'order': order.to_dict(),
            'message': 'Order status updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update order status'}), 500

@orders_bp.route('/orders/<int:order_id>/invoice', methods=['POST'])
@jwt_required()
def create_order_invoice(order_id):
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Calculate invoice details
        amount = float(data.get('amount', order.order_value - order.advance_payment))
        tax_rate = float(data.get('tax_rate', 0.18))  # Default 18% GST
        tax_amount = amount * tax_rate
        total_amount = amount + tax_amount
        
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create invoice
        from models import Invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            order_id=order.id,
            customer_id=order.customer_id,
            amount=amount,
            tax_amount=tax_amount,
            total_amount=total_amount,
            status='pending',
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
            notes=data.get('notes', '')
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        return jsonify({
            'invoice': invoice.to_dict(),
            'message': 'Invoice created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create invoice'}), 500
