from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Delivery, Order, Customer, db
from datetime import datetime, date
import uuid

deliveries_bp = Blueprint('deliveries', __name__)

def generate_delivery_number():
    """Generate unique delivery number"""
    return f"DEL-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

@deliveries_bp.route('/deliveries', methods=['GET'])
@jwt_required()
def get_deliveries():
    try:
        # Get query parameters
        status = request.args.get('status')
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Delivery.query
        
        if status:
            query = query.filter(Delivery.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Delivery.delivery_number.ilike(search_term),
                    Delivery.order.has(Order.order_number.ilike(search_term)),
                    Delivery.order.has(Order.customer_name.ilike(search_term)),
                    Delivery.delivery_address.ilike(search_term)
                )
            )
        
        # Order by delivery date
        query = query.order_by(Delivery.delivery_date.desc())
        
        # Paginate results
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        deliveries = pagination.items
        
        return jsonify({
            'deliveries': [delivery.to_dict() for delivery in deliveries],
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
        return jsonify({'error': 'Failed to fetch deliveries'}), 500

@deliveries_bp.route('/deliveries/<int:delivery_id>', methods=['GET'])
@jwt_required()
def get_delivery(delivery_id):
    try:
        delivery = Delivery.query.get(delivery_id)
        
        if not delivery:
            return jsonify({'error': 'Delivery not found'}), 404
        
        return jsonify({
            'delivery': delivery.to_dict(),
            'message': 'Delivery retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch delivery'}), 500

@deliveries_bp.route('/deliveries', methods=['POST'])
@jwt_required()
def create_delivery():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['order_id', 'customer_id', 'delivery_date', 'delivery_address']
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
        
        # Create new delivery
        delivery = Delivery(
            delivery_number=generate_delivery_number(),
            order_id=data['order_id'],
            customer_id=data['customer_id'],
            delivery_date=datetime.strptime(data['delivery_date'], '%Y-%m-%d').date(),
            delivery_address=data['delivery_address'],
            status=data.get('status', 'scheduled'),
            delivery_person=data.get('delivery_person', ''),
            tracking_number=data.get('tracking_number', ''),
            notes=data.get('notes', '')
        )
        
        db.session.add(delivery)
        db.session.commit()
        
        return jsonify({
            'delivery': delivery.to_dict(),
            'message': 'Delivery created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create delivery'}), 500

@deliveries_bp.route('/deliveries/<int:delivery_id>', methods=['PUT'])
@jwt_required()
def update_delivery(delivery_id):
    try:
        delivery = Delivery.query.get(delivery_id)
        
        if not delivery:
            return jsonify({'error': 'Delivery not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'delivery_date' in data:
            delivery.delivery_date = datetime.strptime(data['delivery_date'], '%Y-%m-%d').date()
        
        if 'delivery_address' in data:
            delivery.delivery_address = data['delivery_address']
        
        if 'status' in data:
            delivery.status = data['status']
        
        if 'delivery_person' in data:
            delivery.delivery_person = data['delivery_person']
        
        if 'tracking_number' in data:
            delivery.tracking_number = data['tracking_number']
        
        if 'notes' in data:
            delivery.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'delivery': delivery.to_dict(),
            'message': 'Delivery updated successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update delivery'}), 500

@deliveries_bp.route('/deliveries/<int:delivery_id>/status', methods=['PUT'])
@jwt_required()
def update_delivery_status(delivery_id):
    try:
        delivery = Delivery.query.get(delivery_id)
        
        if not delivery:
            return jsonify({'error': 'Delivery not found'}), 404
        
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['scheduled', 'in_transit', 'delivered', 'failed']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        delivery.status = data['status']
        
        # If delivered, update the order status as well
        if data['status'] == 'delivered':
            delivery.order.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            'delivery': delivery.to_dict(),
            'message': 'Delivery status updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update delivery status'}), 500

@deliveries_bp.route('/deliveries/<int:delivery_id>', methods=['DELETE'])
@jwt_required()
def delete_delivery(delivery_id):
    try:
        delivery = Delivery.query.get(delivery_id)
        
        if not delivery:
            return jsonify({'error': 'Delivery not found'}), 404
        
        # Check if delivery can be deleted
        if delivery.status == 'delivered':
            return jsonify({'error': 'Cannot delete completed delivery'}), 400
        
        db.session.delete(delivery)
        db.session.commit()
        
        return jsonify({'message': 'Delivery deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete delivery'}), 500

@deliveries_bp.route('/deliveries/stats', methods=['GET'])
@jwt_required()
def get_delivery_stats():
    try:
        from sqlalchemy import func
        
        # Get total deliveries count
        total_deliveries = Delivery.query.count()
        
        # Get scheduled deliveries
        scheduled_deliveries = Delivery.query.filter(Delivery.status == 'scheduled').count()
        
        # Get in transit deliveries
        in_transit_deliveries = Delivery.query.filter(Delivery.status == 'in_transit').count()
        
        # Get delivered deliveries
        delivered_deliveries = Delivery.query.filter(Delivery.status == 'delivered').count()
        
        # Get failed deliveries
        failed_deliveries = Delivery.query.filter(Delivery.status == 'failed').count()
        
        # Get today's deliveries
        today = date.today()
        todays_deliveries = Delivery.query.filter(
            Delivery.delivery_date == today
        ).count()
        
        # Get overdue deliveries (scheduled for past dates but not delivered)
        overdue_deliveries = Delivery.query.filter(
            db.and_(
                Delivery.delivery_date < today,
                Delivery.status.in_(['scheduled', 'in_transit'])
            )
        ).count()
        
        return jsonify({
            'totalDeliveries': total_deliveries,
            'scheduledDeliveries': scheduled_deliveries,
            'inTransitDeliveries': in_transit_deliveries,
            'deliveredDeliveries': delivered_deliveries,
            'failedDeliveries': failed_deliveries,
            'todaysDeliveries': todays_deliveries,
            'overdueDeliveries': overdue_deliveries
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch delivery stats'}), 500

@deliveries_bp.route('/deliveries/today', methods=['GET'])
@jwt_required()
def get_todays_deliveries():
    try:
        today = date.today()
        
        deliveries = Delivery.query.filter(
            Delivery.delivery_date == today
        ).order_by(Delivery.delivery_date).all()
        
        return jsonify({
            'deliveries': [delivery.to_dict() for delivery in deliveries],
            'date': today.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch today\'s deliveries'}), 500
