"""
AI Invoice Generation API Routes
Advanced AI-powered invoice generation endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Order, Customer, Invoice, db
from ai_invoice_generator import (
    ai_invoice_generator, 
    generate_ai_invoice, 
    get_invoice_suggestions
)
import logging

logger = logging.getLogger(__name__)

ai_invoices_bp = Blueprint('ai_invoices', __name__)

@ai_invoices_bp.route('/ai/invoices/suggestions/<int:order_id>', methods=['GET'])
@jwt_required()
def get_ai_invoice_suggestions(order_id):
    """Get AI suggestions for creating an invoice from an order"""
    try:
        suggestions = get_invoice_suggestions(order_id)
        
        if not suggestions:
            return jsonify({'error': 'Order not found or unable to generate suggestions'}), 404
        
        return jsonify({
            'suggestions': suggestions,
            'message': 'AI invoice suggestions generated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting AI suggestions for order {order_id}: {str(e)}")
        return jsonify({'error': 'Failed to generate AI suggestions'}), 500

@ai_invoices_bp.route('/ai/invoices/generate/<int:order_id>', methods=['POST'])
@jwt_required()
def generate_ai_invoice_from_order(order_id):
    """Generate an AI-powered invoice from an order"""
    try:
        data = request.get_json() or {}
        save_to_db = data.get('save_to_db', True)
        auto_calculate = data.get('auto_calculate', True)
        
        # Check if order exists
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check if invoice already exists for this order
        existing_invoice = Invoice.query.filter_by(order_id=order_id).first()
        if existing_invoice:
            return jsonify({
                'error': 'Invoice already exists for this order',
                'existing_invoice_id': existing_invoice.id,
                'invoice_number': existing_invoice.invoice_number
            }), 409
        
        # Generate AI invoice
        generated_invoice = ai_invoice_generator.create_invoice_from_order(
            order_id, auto_calculate=auto_calculate
        )
        
        if not generated_invoice:
            return jsonify({'error': 'Failed to generate AI invoice'}), 500
        
        # Save to database if requested
        saved_invoice = None
        if save_to_db:
            saved_invoice = ai_invoice_generator.save_generated_invoice(
                generated_invoice, order_id
            )
        
        # Prepare response
        response_data = {
            'generated_invoice': {
                'invoice_number': generated_invoice.invoice_number,
                'customer_name': generated_invoice.customer_name,
                'customer_address': generated_invoice.customer_address,
                'items': [
                    {
                        'description': item.description,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'total_price': item.total_price,
                        'tax_rate': item.tax_rate * 100  # Convert to percentage
                    }
                    for item in generated_invoice.items
                ],
                'subtotal': generated_invoice.subtotal,
                'tax_amount': generated_invoice.tax_amount,
                'total_amount': generated_invoice.total_amount,
                'due_date': generated_invoice.due_date.isoformat(),
                'notes': generated_invoice.notes
            },
            'message': 'AI invoice generated successfully'
        }
        
        if saved_invoice:
            response_data['saved_invoice_id'] = saved_invoice.id
        
        return jsonify(response_data), 201
        
    except Exception as e:
        logger.error(f"Error generating AI invoice for order {order_id}: {str(e)}")
        return jsonify({'error': 'Failed to generate AI invoice'}), 500

@ai_invoices_bp.route('/ai/invoices/bulk-generate', methods=['POST'])
@jwt_required()
def bulk_generate_ai_invoices():
    """Generate AI invoices for multiple orders"""
    try:
        data = request.get_json()
        
        if not data or 'order_ids' not in data:
            return jsonify({'error': 'order_ids is required'}), 400
        
        order_ids = data['order_ids']
        save_to_db = data.get('save_to_db', True)
        
        if not isinstance(order_ids, list):
            return jsonify({'error': 'order_ids must be an array'}), 400
        
        # Validate orders exist
        existing_orders = Order.query.filter(Order.id.in_(order_ids)).all()
        if len(existing_orders) != len(order_ids):
            return jsonify({'error': 'Some orders not found'}), 404
        
        # Generate invoices
        generated_invoices = ai_invoice_generator.bulk_generate_invoices(order_ids)
        
        # Save to database if requested
        saved_invoices = []
        if save_to_db:
            for i, generated in enumerate(generated_invoices):
                if generated:
                    saved = ai_invoice_generator.save_generated_invoice(
                        generated, order_ids[i]
                    )
                    if saved:
                        saved_invoices.append(saved)
        
        return jsonify({
            'generated_count': len(generated_invoices),
            'saved_count': len(saved_invoices),
            'generated_invoices': [
                {
                    'invoice_number': inv.invoice_number,
                    'total_amount': inv.total_amount,
                    'customer_name': inv.customer_name
                }
                for inv in generated_invoices if inv
            ],
            'message': f'Successfully generated {len(generated_invoices)} AI invoices'
        }), 201
        
    except Exception as e:
        logger.error(f"Error bulk generating AI invoices: {str(e)}")
        return jsonify({'error': 'Failed to bulk generate AI invoices'}), 500

@ai_invoices_bp.route('/ai/invoices/analyze-order/<int:order_id>', methods=['GET'])
@jwt_required()
def analyze_order_for_invoice(order_id):
    """Analyze an order using AI for invoice generation insights"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Perform AI analysis
        analysis = ai_invoice_generator.analyze_order_content(order)
        
        # Get detailed description
        description = ai_invoice_generator.generate_invoice_description(order)
        
        return jsonify({
            'order_id': order_id,
            'analysis': analysis,
            'description': description,
            'recommendations': {
                'estimated_completion_hours': analysis['estimated_hours'],
                'complexity_level': analysis['complexity'],
                'suggested_tax_rate': analysis['tax_rate'] * 100,
                'material_labor_split': {
                    'material_percentage': analysis['material_cost_ratio'] * 100,
                    'labor_percentage': analysis['labor_cost_ratio'] * 100
                }
            },
            'message': 'Order analysis completed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing order {order_id}: {str(e)}")
        return jsonify({'error': 'Failed to analyze order'}), 500

@ai_invoices_bp.route('/ai/invoices/smart-pricing', methods=['POST'])
@jwt_required()
def calculate_smart_pricing():
    """Calculate smart pricing using AI for given items"""
    try:
        data = request.get_json()
        
        if not data or 'items' not in data:
            return jsonify({'error': 'items is required'}), 400
        
        items_data = data['items']
        
        # Convert to InvoiceItem objects
        from ai_invoice_generator import InvoiceItem
        items = []
        for item_data in items_data:
            item = InvoiceItem(
                description=item_data.get('description', ''),
                quantity=int(item_data.get('quantity', 1)),
                unit_price=float(item_data.get('unit_price', 0)),
                total_price=float(item_data.get('total_price', 0)),
                tax_rate=float(item_data.get('tax_rate', 0.18))
            )
            items.append(item)
        
        # Calculate intelligent pricing
        subtotal, tax_amount, total_amount = ai_invoice_generator.calculate_intelligent_pricing(items)
        
        return jsonify({
            'pricing': {
                'subtotal': subtotal,
                'tax_amount': tax_amount,
                'total_amount': total_amount,
                'tax_breakdown': [
                    {
                        'description': item.description,
                        'tax_rate': item.tax_rate * 100,
                        'tax_amount': item.total_price * item.tax_rate
                    }
                    for item in items
                ]
            },
            'message': 'Smart pricing calculated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating smart pricing: {str(e)}")
        return jsonify({'error': 'Failed to calculate smart pricing'}), 500

@ai_invoices_bp.route('/ai/invoices/templates', methods=['GET'])
@jwt_required()
def get_invoice_templates():
    """Get AI-generated invoice templates for different textile categories"""
    try:
        templates = {
            'shirt_tailoring': {
                'items': [
                    {'description': 'Custom Shirt - Premium Fabric', 'unit_price': 1200, 'tax_rate': 0.12},
                    {'description': 'Tailoring Services - Standard', 'unit_price': 800, 'tax_rate': 0.18}
                ],
                'notes': 'Premium shirt tailoring with custom measurements.'
            },
            'suit_tailoring': {
                'items': [
                    {'description': 'Custom Suit - Premium Fabric', 'unit_price': 5000, 'tax_rate': 0.12},
                    {'description': 'Complex Tailoring Services', 'unit_price': 3000, 'tax_rate': 0.18},
                    {'description': 'Premium Finishing', 'unit_price': 1000, 'tax_rate': 0.18}
                ],
                'notes': 'Complex suit tailoring requiring expert craftsmanship. Estimated completion time: 8 hours.'
            },
            'saree_services': {
                'items': [
                    {'description': 'Saree Fabric - Silk', 'unit_price': 3000, 'tax_rate': 0.05},
                    {'description': 'Blouse Stitching', 'unit_price': 800, 'tax_rate': 0.18},
                    {'description': 'Fall & Pico Work', 'unit_price': 200, 'tax_rate': 0.18}
                ],
                'notes': 'Premium quality silk saree with professional blouse stitching.'
            },
            'alteration_services': {
                'items': [
                    {'description': 'Garment Alteration Services', 'unit_price': 300, 'tax_rate': 0.18}
                ],
                'notes': 'Quick alteration services with standard processing timeline.'
            }
        }
        
        return jsonify({
            'templates': templates,
            'message': 'Invoice templates retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting invoice templates: {str(e)}")
        return jsonify({'error': 'Failed to get invoice templates'}), 500

@ai_invoices_bp.route('/ai/invoices/stats', methods=['GET'])
@jwt_required()
def get_ai_invoice_stats():
    """Get statistics about AI-generated invoices"""
    try:
        # Get all invoices that start with TSI (TEX-SARTHI AI Invoice)
        ai_invoices = Invoice.query.filter(Invoice.invoice_number.like('TSI-%')).all()
        
        total_ai_invoices = len(ai_invoices)
        total_ai_amount = sum(inv.total_amount for inv in ai_invoices)
        
        # Calculate average amounts
        avg_amount = total_ai_amount / total_ai_invoices if total_ai_invoices > 0 else 0
        
        # Status breakdown
        status_counts = {}
        for invoice in ai_invoices:
            status_counts[invoice.status] = status_counts.get(invoice.status, 0) + 1
        
        return jsonify({
            'stats': {
                'total_ai_invoices': total_ai_invoices,
                'total_ai_amount': total_ai_amount,
                'average_amount': avg_amount,
                'status_breakdown': status_counts
            },
            'message': 'AI invoice statistics retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting AI invoice stats: {str(e)}")
        return jsonify({'error': 'Failed to get AI invoice stats'}), 500