from flask import Blueprint, request, jsonify, send_file, make_response
from flask_jwt_extended import jwt_required
from models import Invoice, Order, Customer, db
from sqlalchemy import or_, and_
from datetime import datetime, date
import uuid
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

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

@invoices_bp.route('/invoices/<int:invoice_id>/view', methods=['GET'])
@jwt_required(optional=True)
def view_invoice(invoice_id):
    """Get detailed invoice information for viewing"""
    try:
        invoice = Invoice.query.get(invoice_id)
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Get related order and customer details
        order = Order.query.get(invoice.order_id)
        customer = Customer.query.get(invoice.customer_id)
        
        invoice_data = invoice.to_dict()
        invoice_data['order'] = order.to_dict() if order else None
        invoice_data['customer'] = customer.to_dict() if customer else None
        
        return jsonify({
            'invoice': invoice_data,
            'message': 'Invoice details retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch invoice details'}), 500

@invoices_bp.route('/invoices/<int:invoice_id>/download', methods=['GET'])
@jwt_required(optional=True)
def download_invoice_pdf(invoice_id):
    """Download invoice as PDF"""
    try:
        invoice = Invoice.query.get(invoice_id)
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Get related order and customer details
        order = Order.query.get(invoice.order_id)
        customer = Customer.query.get(invoice.customer_id)
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Company Header with prominent TEX-SARTHI branding
        header_style = ParagraphStyle(
            'CompanyHeader',
            parent=styles['Heading1'],
            fontSize=36,
            spaceAfter=15,
            alignment=1,  # Center alignment
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        company_style = ParagraphStyle(
            'CompanyInfo',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=8,
            alignment=1,
            textColor=colors.darkgrey,
            fontName='Helvetica'
        )
        
        tagline_style = ParagraphStyle(
            'CompanyTagline',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=5,
            alignment=1,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # Add a decorative line above the company name
        story.append(Spacer(1, 10))
        story.append(Paragraph("─" * 50, ParagraphStyle('Line', fontSize=8, alignment=1, textColor=colors.darkblue)))
        story.append(Spacer(1, 5))
        
        # Prominent TEX-SARTHI branding
        story.append(Paragraph("TEX-SARTHI", header_style))
        story.append(Paragraph("Textile & Garment Solutions", company_style))
        story.append(Paragraph("Professional Tailoring Services", tagline_style))
        story.append(Paragraph("Quality Tailoring • Custom Fitting • Professional Service", company_style))
        
        # Add a decorative line below the company info
        story.append(Paragraph("─" * 50, ParagraphStyle('Line', fontSize=8, alignment=1, textColor=colors.darkblue)))
        story.append(Spacer(1, 20))
        
        # Invoice Title
        invoice_title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            alignment=1,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph("INVOICE", invoice_title_style))
        
        # Invoice and Bill To sections side by side
        invoice_info = [
            ['Invoice Number:', invoice.invoice_number],
            ['Invoice Date:', invoice.created_at.strftime('%B %d, %Y')],
            ['Due Date:', invoice.due_date.strftime('%B %d, %Y') if invoice.due_date else 'N/A'],
            ['Status:', invoice.status.upper()]
        ]
        
        if order:
            invoice_info.extend([
                ['Order Number:', order.order_number],
                ['Order Date:', order.created_at.strftime('%B %d, %Y')],
                ['Delivery Date:', order.delivery_date.strftime('%B %d, %Y') if order.delivery_date else 'N/A']
            ])
        
        # Customer information
        customer_info = []
        if customer:
            customer_info = [
                ['Bill To:', ''],
                ['Name:', customer.name],
                ['Phone:', customer.phone or 'N/A'],
                ['Email:', customer.email or 'N/A'],
                ['Address:', customer.address or 'N/A']
            ]
        
        # Create two-column layout
        invoice_table = Table(invoice_info, colWidths=[1.5*inch, 2.5*inch])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        customer_table = Table(customer_info, colWidths=[1.5*inch, 2.5*inch]) if customer_info else None
        if customer_table:
            customer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.darkgreen),
                ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
        
        # Add tables side by side
        if customer_table:
            combined_table = Table([[invoice_table, customer_table]], colWidths=[4*inch, 4*inch])
            combined_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            story.append(combined_table)
        else:
            story.append(invoice_table)
        
        story.append(Spacer(1, 30))
        
        # Order details with professional styling
        if order:
            section_style = ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=10,
                textColor=colors.darkblue,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph("Order Details", section_style))
            
            order_data = [
                ['Item Type:', order.order_type or 'N/A'],
                ['Fabric:', order.fabric or 'N/A'],
                ['Color:', order.color or 'N/A'],
                ['Quantity:', str(order.quantity)],
                ['Order Value:', f"₹{order.order_value:,.2f}"],
                ['Advance Paid:', f"₹{order.advance_payment or 0:,.2f}"],
                ['Notes:', order.notes or 'N/A']
            ]
            
            order_table = Table(order_data, colWidths=[1.5*inch, 4*inch])
            order_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(order_table)
            story.append(Spacer(1, 30))
        
        # Professional amount details section
        story.append(Paragraph("Amount Details", section_style))
        
        # Create a more professional amount table
        amount_data = [
            ['Description', 'Amount'],
            ['Subtotal', f"₹{invoice.amount:,.2f}"],
            ['GST (18%)', f"₹{invoice.tax_amount:,.2f}"],
            ['', ''],  # Empty row for spacing
            ['TOTAL AMOUNT', f"₹{invoice.total_amount:,.2f}"]
        ]
        
        amount_table = Table(amount_data, colWidths=[3*inch, 2*inch])
        amount_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('BACKGROUND', (0, 1), (0, -2), colors.lightgrey),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 11),
            ('ALIGN', (0, 1), (0, -2), 'LEFT'),
            ('ALIGN', (1, 1), (1, -2), 'RIGHT'),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 8),
            ('TOPPADDING', (0, 1), (-1, -2), 8),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.darkgreen),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 15),
            ('TOPPADDING', (0, -1), (-1, -1), 15),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(amount_table)
        story.append(Spacer(1, 30))
        
        # Notes section
        if invoice.notes:
            story.append(Paragraph("Additional Notes", section_style))
            notes_style = ParagraphStyle(
                'Notes',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=10,
                textColor=colors.darkgrey,
                fontName='Helvetica',
                leftIndent=20,
                rightIndent=20,
                borderWidth=1,
                borderColor=colors.lightgrey,
                borderPadding=10,
                backColor=colors.lightgrey
            )
            story.append(Paragraph(invoice.notes, notes_style))
            story.append(Spacer(1, 20))
        
        # Professional footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=10,
            textColor=colors.darkgrey,
            fontName='Helvetica',
            alignment=1  # Center alignment
        )
        
        story.append(Spacer(1, 40))
        
        # Add decorative line before footer
        story.append(Paragraph("─" * 50, ParagraphStyle('Line', fontSize=8, alignment=1, textColor=colors.darkblue)))
        story.append(Spacer(1, 10))
        
        # Professional footer with TEX-SARTHI branding
        story.append(Paragraph("Thank you for choosing TEX-SARTHI!", footer_style))
        story.append(Paragraph("TEX-SARTHI - Professional Tailoring Services", footer_style))
        story.append(Paragraph("Quality Tailoring • Custom Fitting • Professional Service", footer_style))
        story.append(Paragraph("For any queries, please contact us", footer_style))
        
        # Add TEX-SARTHI branding at the bottom
        footer_brand_style = ParagraphStyle(
            'FooterBrand',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=5,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold',
            alignment=1
        )
        story.append(Spacer(1, 10))
        story.append(Paragraph("TEX-SARTHI", footer_brand_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Create response
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=invoice_{invoice.invoice_number}.pdf'
        
        return response
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate PDF'}), 500

