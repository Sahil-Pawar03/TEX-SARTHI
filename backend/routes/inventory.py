from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import InventoryItem, db
from sqlalchemy import func

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory', methods=['GET'])
@jwt_required(optional=True)
def get_inventory():
    try:
        # Get query parameters
        type_filter = request.args.get('type')
        search = request.args.get('search')
        status = request.args.get('status')
        low_stock = request.args.get('low_stock', 'false').lower() == 'true'
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = InventoryItem.query
        
        if type_filter:
            query = query.filter(InventoryItem.type == type_filter)
        
        if status:
            query = query.filter(InventoryItem.status == status)
        
        if low_stock:
            query = query.filter(InventoryItem.current_stock <= InventoryItem.min_stock)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    InventoryItem.item_name.ilike(search_term),
                    InventoryItem.color.ilike(search_term),
                    InventoryItem.supplier.ilike(search_term)
                )
            )
        
        # Order by item name
        query = query.order_by(InventoryItem.item_name)
        
        # Paginate results
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        items = pagination.items
        
        return jsonify({
            'inventory': [item.to_dict() for item in items],
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
        return jsonify({'error': 'Failed to fetch inventory'}), 500

@inventory_bp.route('/inventory/<int:item_id>', methods=['GET'])
@jwt_required(optional=True)
def get_inventory_item(item_id):
    try:
        item = InventoryItem.query.get(item_id)
        
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
        
        return jsonify({
            'item': item.to_dict(),
            'message': 'Inventory item retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch inventory item'}), 500

@inventory_bp.route('/inventory', methods=['POST'])
@jwt_required(optional=True)
def create_inventory_item():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['item_name', 'type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new inventory item
        item = InventoryItem(
            item_name=data['item_name'],
            type=data['type'],
            color=data.get('color', ''),
            current_stock=int(data.get('current_stock', 0)),
            min_stock=int(data.get('min_stock', 0)),
            cost_per_unit=float(data.get('cost_per_unit', 0.0)),
            supplier=data.get('supplier', ''),
            status=data.get('status', 'in_stock')
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'item': item.to_dict(),
            'message': 'Inventory item created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid numeric value'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create inventory item'}), 500

@inventory_bp.route('/inventory/<int:item_id>', methods=['PUT'])
@jwt_required(optional=True)
def update_inventory_item(item_id):
    try:
        item = InventoryItem.query.get(item_id)
        
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'item_name' in data:
            item.item_name = data['item_name']
        
        if 'type' in data:
            item.type = data['type']
        
        if 'color' in data:
            item.color = data['color']
        
        if 'current_stock' in data:
            item.current_stock = int(data['current_stock'])
        
        if 'min_stock' in data:
            item.min_stock = int(data['min_stock'])
        
        if 'cost_per_unit' in data:
            item.cost_per_unit = float(data['cost_per_unit'])
        
        if 'supplier' in data:
            item.supplier = data['supplier']
        
        if 'status' in data:
            item.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'item': item.to_dict(),
            'message': 'Inventory item updated successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid numeric value'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update inventory item'}), 500

@inventory_bp.route('/inventory/<int:item_id>', methods=['DELETE'])
@jwt_required(optional=True)
def delete_inventory_item(item_id):
    try:
        item = InventoryItem.query.get(item_id)
        
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'message': 'Inventory item deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete inventory item'}), 500

@inventory_bp.route('/inventory/<int:item_id>/stock', methods=['PUT'])
@jwt_required(optional=True)
def update_stock(item_id):
    try:
        item = InventoryItem.query.get(item_id)
        
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
        
        data = request.get_json()
        
        if not data or 'quantity' not in data:
            return jsonify({'error': 'Quantity is required'}), 400
        
        operation = data.get('operation', 'add')  # add, subtract, set
        quantity = int(data['quantity'])
        
        if operation == 'add':
            item.current_stock += quantity
        elif operation == 'subtract':
            item.current_stock = max(0, item.current_stock - quantity)
        elif operation == 'set':
            item.current_stock = max(0, quantity)
        else:
            return jsonify({'error': 'Invalid operation. Must be add, subtract, or set'}), 400
        
        # Update status based on stock level
        if item.current_stock <= 0:
            item.status = 'out_of_stock'
        elif item.current_stock <= item.min_stock:
            item.status = 'low_stock'
        else:
            item.status = 'in_stock'
        
        db.session.commit()
        
        return jsonify({
            'item': item.to_dict(),
            'message': 'Stock updated successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid quantity value'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update stock'}), 500

@inventory_bp.route('/inventory/stats', methods=['GET'])
@jwt_required(optional=True)
def get_inventory_stats():
    try:
        # Get total items count
        total_items = InventoryItem.query.count()
        
        # Get low stock items
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.min_stock
        ).count()
        
        # Get out of stock items
        out_of_stock_items = InventoryItem.query.filter(
            InventoryItem.current_stock == 0
        ).count()
        
        # Get total inventory value
        total_value = db.session.query(func.sum(
            InventoryItem.current_stock * InventoryItem.cost_per_unit
        )).scalar() or 0
        
        # Get items by type
        items_by_type = db.session.query(
            InventoryItem.type,
            func.count(InventoryItem.id).label('count'),
            func.sum(InventoryItem.current_stock * InventoryItem.cost_per_unit).label('value')
        ).group_by(InventoryItem.type).all()
        
        # Get items by status
        items_by_status = db.session.query(
            InventoryItem.status,
            func.count(InventoryItem.id).label('count')
        ).group_by(InventoryItem.status).all()
        
        # Get low stock items details
        low_stock_details = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.min_stock
        ).all()
        
        return jsonify({
            'totalItems': total_items,
            'lowStockItems': low_stock_items,
            'outOfStockItems': out_of_stock_items,
            'totalValue': float(total_value),
            'itemsByType': [
                {
                    'type': item[0],
                    'count': item[1],
                    'value': float(item[2]) if item[2] else 0
                }
                for item in items_by_type
            ],
            'itemsByStatus': [
                {
                    'status': status[0],
                    'count': status[1]
                }
                for status in items_by_status
            ],
            'lowStockDetails': [item.to_dict() for item in low_stock_details]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch inventory stats'}), 500

@inventory_bp.route('/inventory/types', methods=['GET'])
@jwt_required(optional=True)
def get_inventory_types():
    try:
        # Get unique inventory types
        types = db.session.query(InventoryItem.type).distinct().all()
        
        return jsonify({
            'types': [type[0] for type in types if type[0]]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch inventory types'}), 500
