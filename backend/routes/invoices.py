from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Invoice, Order, Customer, db
from sqlalchemy import or_, and_
from datetime import datetime, date
import uuid

# Import AI invoice generator for integration
try:
    from ai_invoice_generator import generate_ai_invoice, get_invoice_suggestions
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

invoices_bp = Blueprint('invoices', __name__)

def generate_invoice_number():
    """Generate unique invoice number"""
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

@invoices_bp.route('/invoices', methods=['GET'])
@jwt_required(optional=True)
def get_invoices():
    try:
        # Get query parameters
        status = request.args.get('status')
        customer_id = request.args.get('customer_id', type=int)
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Invoice.query
        
        if status:
            query = query.filter(Invoice.status == status)
        if customer_id:
            query = query.filter(Invoice.customer_id == customer_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Invoice.invoice_number.ilike(search_term),
                    Invoice.order.has(Order.order_number.ilike(search_term)),
                    Invoice.order.has(Order.customer_name.ilike(search_term))
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(Invoice.created_at.desc())
        
        # Paginate results
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        invoices = pagination.items
        
        return jsonify({
            'invoices': [invoice.to_dict() for invoice in invoices],
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
        return jsonify({'error': 'Failed to fetch invoices'}), 500

@invoices_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
@jwt_required(optional=True)
def get_invoice(invoice_id):
    try:
        invoice = Invoice.query.get(invoice_id)
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        return jsonify({
            'invoice': invoice.to_dict(),
            'message': 'Invoice retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch invoice'}), 500

@invoices_bp.route('/invoices', methods=['POST'])
@jwt_required()
def create_invoice():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['order_id', 'customer_id', 'amount']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if order exists
        order = Order.query.get(data['order_id'])
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check if customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Calculate invoice details
        amount = float(data['amount'])
        tax_rate = float(data.get('tax_rate', 0.18))  # Default 18% GST
        tax_amount = amount * tax_rate
        total_amount = amount + tax_amount
        
        # Create new invoice
        invoice = Invoice(
            invoice_number=generate_invoice_number(),
            order_id=data['order_id'],
            customer_id=data['customer_id'],
            amount=amount,
            tax_amount=tax_amount,
            total_amount=total_amount,
            status=data.get('status', 'pending'),
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

@invoices_bp.route('/invoices/by-order-number', methods=['POST'])
@jwt_required(optional=True)
def create_invoice_by_order_number():
    """Create an invoice given only an order_number; derive values from the order."""
    try:
        payload = request.get_json(silent=True) or {}
        order_number = (payload.get('order_number') or '').strip()
        if not order_number:
            return jsonify({'error': 'order_number is required'}), 400

        order = Order.query.filter(Order.order_number.ilike(order_number)).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Ensure customer exists
        customer = Customer.query.get(order.customer_id)
        if not customer:
            customer = Customer(name=order.customer_name or 'Customer')
            db.session.add(customer)
            db.session.flush()
            order.customer_id = customer.id

        # Calculate amounts
        amount = float((order.order_value or 0) - (order.advance_payment or 0))
        if amount < 0:
            amount = 0.0
        tax_rate = float(payload.get('tax_rate', 0.18))
        tax_amount = amount * tax_rate
        total_amount = amount + tax_amount

        due_date = None
        if payload.get('due_date'):
            try:
                due_date = datetime.strptime(payload['due_date'], '%Y-%m-%d').date()
            except Exception:
                due_date = None

        invoice = Invoice(
            invoice_number=generate_invoice_number(),
            order_id=order.id,
            customer_id=order.customer_id,
            amount=amount,
            tax_amount=tax_amount,
            total_amount=total_amount,
            status='pending',
            due_date=due_date,
            notes=payload.get('notes', '')
        )

        db.session.add(invoice)
        db.session.commit()

        return jsonify({'invoice': invoice.to_dict(), 'message': 'Invoice created successfully'}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Failed to create invoice by order number'}), 500

@invoices_bp.route('/invoices/<int:invoice_id>', methods=['PUT'])
@jwt_required()
def update_invoice(invoice_id):
    try:
        invoice = Invoice.query.get(invoice_id)
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'amount' in data:
            amount = float(data['amount'])
            tax_rate = float(data.get('tax_rate', 0.18))
            invoice.amount = amount
            invoice.tax_amount = amount * tax_rate
            invoice.total_amount = amount + invoice.tax_amount
        
        if 'status' in data:
            invoice.status = data['status']
            if data['status'] == 'paid':
                invoice.paid_date = date.today()
        
        if 'due_date' in data:
            if data['due_date']:
                invoice.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            else:
                invoice.due_date = None
        
        if 'payment_method' in data:
            invoice.payment_method = data['payment_method']
        
        if 'notes' in data:
            invoice.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'invoice': invoice.to_dict(),
            'message': 'Invoice updated successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update invoice'}), 500

@invoices_bp.route('/invoices/ai-available', methods=['GET'])
@jwt_required()
def check_ai_availability():
    """Check if AI invoice generation is available"""
    return jsonify({
        'ai_available': AI_AVAILABLE,
        'message': 'AI invoice generation is available' if AI_AVAILABLE else 'AI invoice generation is not available'
    }), 200

@invoices_bp.route('/invoices/<int:invoice_id>/pay', methods=['PUT'])
@jwt_required()
def mark_invoice_paid(invoice_id):
    try:
        invoice = Invoice.query.get(invoice_id)
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Mark invoice as paid
        invoice.status = 'paid'
        invoice.paid_date = date.today()
        invoice.payment_method = data.get('payment_method', '')
        
        if data.get('notes'):
            invoice.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'invoice': invoice.to_dict(),
            'message': 'Invoice marked as paid successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to mark invoice as paid'}), 500

@invoices_bp.route('/invoices/<int:invoice_id>', methods=['DELETE'])
@jwt_required()
def delete_invoice(invoice_id):
    try:
        invoice = Invoice.query.get(invoice_id)
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Check if invoice can be deleted
        if invoice.status == 'paid':
            return jsonify({'error': 'Cannot delete paid invoice'}), 400
        
        db.session.delete(invoice)
        db.session.commit()
        
        return jsonify({'message': 'Invoice deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete invoice'}), 500

@invoices_bp.route('/invoices/stats', methods=['GET'])
@jwt_required(optional=True)
def get_invoice_stats():
    try:
        from sqlalchemy import func
        
        # Get total invoices count
        total_invoices = Invoice.query.count()
        
        # Get pending invoices
        pending_invoices = Invoice.query.filter(Invoice.status == 'pending').count()
        
        # Get paid invoices
        paid_invoices = Invoice.query.filter(Invoice.status == 'paid').count()
        
        # Get overdue invoices
        overdue_invoices = Invoice.query.filter(
            and_(
                Invoice.status == 'pending',
                Invoice.due_date < date.today()
            )
        ).count()
        
        # Get total outstanding amount
        outstanding_amount = db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.status == 'pending'
        ).scalar() or 0
        
        # Get total collected amount
        collected_amount = db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.status == 'paid'
        ).scalar() or 0
        
        # Get monthly revenue
        current_month = datetime.now().replace(day=1)
        monthly_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.status == 'paid',
                Invoice.paid_date >= current_month
            )
        ).scalar() or 0
        
        return jsonify({
            'totalInvoices': total_invoices,
            'pendingInvoices': pending_invoices,
            'paidInvoices': paid_invoices,
            'overdueInvoices': overdue_invoices,
            'outstandingAmount': float(outstanding_amount),
            'collectedAmount': float(collected_amount),
            'monthlyRevenue': float(monthly_revenue)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch invoice stats'}), 500
