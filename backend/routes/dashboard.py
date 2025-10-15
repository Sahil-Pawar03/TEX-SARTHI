from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import Order, InventoryItem, Delivery, Invoice, db
from sqlalchemy import func, and_
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required(optional=True)
def get_dashboard_stats():
    try:
        # Get total orders count
        total_orders = Order.query.count()
        
        # Get low stock items (current_stock <= min_stock)
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.min_stock
        ).count()
        
        # Get pending deliveries
        pending_deliveries = Delivery.query.filter(
            Delivery.status.in_(['scheduled', 'in_transit'])
        ).count()
        
        # Get outstanding amount (sum of unpaid invoices)
        outstanding_invoices = Invoice.query.filter(
            Invoice.status.in_(['pending', 'overdue'])
        ).all()
        outstanding_amount = sum(invoice.total_amount for invoice in outstanding_invoices)
        
        # Get recent orders (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_orders = Order.query.filter(
            Order.created_at >= week_ago
        ).count()
        
        # Get completed orders this month
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        completed_orders_this_month = Order.query.filter(
            and_(
                Order.status == 'completed',
                Order.created_at >= month_start
            )
        ).count()
        
        # Get total revenue this month
        monthly_revenue = db.session.query(func.sum(Order.order_value)).filter(
            and_(
                Order.status == 'completed',
                Order.created_at >= month_start
            )
        ).scalar() or 0
        
        # Get top customers by order count
        top_customers = db.session.query(
            Order.customer_name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.order_value).label('total_value')
        ).filter(
            Order.status == 'completed'
        ).group_by(Order.customer_name).order_by(
            func.count(Order.id).desc()
        ).limit(5).all()
        
        # Get order status distribution
        status_distribution = db.session.query(
            Order.status,
            func.count(Order.id).label('count')
        ).group_by(Order.status).all()
        
        # Get inventory status distribution
        inventory_status = db.session.query(
            InventoryItem.status,
            func.count(InventoryItem.id).label('count')
        ).group_by(InventoryItem.status).all()
        
        # Get recent activity (last 10 orders)
        recent_activity = Order.query.order_by(
            Order.created_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'totalOrders': total_orders,
            'lowStockItems': low_stock_items,
            'pendingDeliveries': pending_deliveries,
            'outstandingAmount': outstanding_amount,
            'recentOrders': recent_orders,
            'completedOrdersThisMonth': completed_orders_this_month,
            'monthlyRevenue': monthly_revenue,
            'topCustomers': [
                {
                    'name': customer[0],
                    'orderCount': customer[1],
                    'totalValue': customer[2]
                }
                for customer in top_customers
            ],
            'statusDistribution': [
                {
                    'status': status[0],
                    'count': status[1]
                }
                for status in status_distribution
            ],
            'inventoryStatus': [
                {
                    'status': status[0],
                    'count': status[1]
                }
                for status in inventory_status
            ],
            'recentActivity': [
                {
                    'id': order.id,
                    'orderNumber': order.order_number,
                    'customerName': order.customer_name,
                    'orderType': order.order_type,
                    'status': order.status,
                    'orderValue': order.order_value,
                    'createdAt': order.created_at.isoformat() if order.created_at else None
                }
                for order in recent_activity
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch dashboard stats'}), 500

@dashboard_bp.route('/dashboard/charts/sales', methods=['GET'])
@jwt_required(optional=True)
def get_sales_chart_data():
    try:
        # Get sales data for the last 12 months
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        
        # Monthly sales data
        monthly_sales = db.session.query(
            func.date_trunc('month', Order.created_at).label('month'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.order_value).label('total_revenue')
        ).filter(
            and_(
                Order.status == 'completed',
                Order.created_at >= twelve_months_ago
            )
        ).group_by(
            func.date_trunc('month', Order.created_at)
        ).order_by('month').all()
        
        # Daily sales for current month
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        daily_sales = db.session.query(
            func.date(Order.created_at).label('day'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.order_value).label('total_revenue')
        ).filter(
            and_(
                Order.status == 'completed',
                Order.created_at >= month_start
            )
        ).group_by(
            func.date(Order.created_at)
        ).order_by('day').all()
        
        return jsonify({
            'monthlySales': [
                {
                    'month': sale[0].strftime('%Y-%m') if sale[0] else None,
                    'orderCount': sale[1],
                    'totalRevenue': float(sale[2]) if sale[2] else 0
                }
                for sale in monthly_sales
            ],
            'dailySales': [
                {
                    'day': sale[0].strftime('%Y-%m-%d') if sale[0] else None,
                    'orderCount': sale[1],
                    'totalRevenue': float(sale[2]) if sale[2] else 0
                }
                for sale in daily_sales
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch sales chart data'}), 500

@dashboard_bp.route('/dashboard/charts/orders', methods=['GET'])
@jwt_required(optional=True)
def get_orders_chart_data():
    try:
        # Get order status distribution
        status_distribution = db.session.query(
            Order.status,
            func.count(Order.id).label('count')
        ).group_by(Order.status).all()
        
        # Get order type distribution
        type_distribution = db.session.query(
            Order.order_type,
            func.count(Order.id).label('count')
        ).group_by(Order.order_type).all()
        
        # Get orders by month for the last 6 months
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        monthly_orders = db.session.query(
            func.date_trunc('month', Order.created_at).label('month'),
            func.count(Order.id).label('order_count')
        ).filter(
            Order.created_at >= six_months_ago
        ).group_by(
            func.date_trunc('month', Order.created_at)
        ).order_by('month').all()
        
        return jsonify({
            'statusDistribution': [
                {
                    'status': status[0],
                    'count': status[1]
                }
                for status in status_distribution
            ],
            'typeDistribution': [
                {
                    'type': type[0],
                    'count': type[1]
                }
                for type in type_distribution
            ],
            'monthlyOrders': [
                {
                    'month': order[0].strftime('%Y-%m') if order[0] else None,
                    'orderCount': order[1]
                }
                for order in monthly_orders
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch orders chart data'}), 500
