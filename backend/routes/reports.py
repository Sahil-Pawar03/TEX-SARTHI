from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Order, Invoice, Delivery, Customer, InventoryItem, db
from sqlalchemy import func, and_, extract
from datetime import datetime, date, timedelta

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/sales', methods=['GET'])
@jwt_required(optional=True)
def get_sales_report():
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        period = request.args.get('period', 'monthly')  # daily, weekly, monthly, yearly
        
        # Set default date range if not provided
        if not end_date:
            end_date = date.today()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if not start_date:
            if period == 'daily':
                start_date = end_date - timedelta(days=30)
            elif period == 'weekly':
                start_date = end_date - timedelta(weeks=12)
            elif period == 'monthly':
                start_date = end_date - timedelta(days=365)
            else:  # yearly
                start_date = end_date - timedelta(days=365*5)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        # Build base query for completed orders
        base_query = Order.query.filter(
            and_(
                Order.status == 'completed',
                Order.created_at >= start_date,
                Order.created_at <= end_date + timedelta(days=1)
            )
        )
        
        # Get sales data based on period (DB-agnostic: compute in Python to support SQLite/Postgres)
        completed_orders = Order.query.filter(
            and_(
                Order.status == 'completed',
                Order.created_at >= start_date,
                Order.created_at <= end_date + timedelta(days=1)
            )
        ).all()

        from collections import defaultdict
        buckets = defaultdict(lambda: {'count': 0, 'sum': 0.0})

        def week_start(d):
            # ISO week starting Monday
            base = d - timedelta(days=d.weekday())
            return base.replace(hour=0, minute=0, second=0, microsecond=0)

        for o in completed_orders:
            dt = o.created_at or datetime.utcnow()
            if period == 'daily':
                key = dt.date().isoformat()
            elif period == 'weekly':
                key = week_start(dt).date().isoformat()
            elif period == 'monthly':
                key = dt.strftime('%Y-%m')
            else:  # yearly
                key = dt.strftime('%Y')
            buckets[key]['count'] += 1
            buckets[key]['sum'] += float(o.order_value or 0)

        # Build sorted list
        def sort_key(k):
            try:
                if period == 'daily' or period == 'weekly':
                    return datetime.strptime(k, '%Y-%m-%d')
                if period == 'monthly':
                    return datetime.strptime(k, '%Y-%m')
                return datetime.strptime(k, '%Y')
            except Exception:
                return datetime.utcnow()

        ordered_keys = sorted(buckets.keys(), key=sort_key)
        sales_data = []
        for k in ordered_keys:
            count = buckets[k]['count']
            total = buckets[k]['sum']
            avg = total / count if count else 0
            # Create a tuple-like structure similar to previous queries
            if period == 'daily' or period == 'weekly':
                dt_obj = datetime.strptime(k, '%Y-%m-%d')
            elif period == 'monthly':
                dt_obj = datetime.strptime(k, '%Y-%m')
            else:
                dt_obj = datetime.strptime(k, '%Y')
            sales_data.append((dt_obj, count, total, avg))
        
        # Get top customers
        top_customers = db.session.query(
            Order.customer_name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.order_value).label('total_spent')
        ).filter(
            and_(
                Order.status == 'completed',
                Order.created_at >= start_date,
                Order.created_at <= end_date + timedelta(days=1)
            )
        ).group_by(Order.customer_name).order_by(
            func.sum(Order.order_value).desc()
        ).limit(10).all()
        
        # Get order type distribution
        order_types = db.session.query(
            Order.order_type,
            func.count(Order.id).label('count'),
            func.sum(Order.order_value).label('revenue')
        ).filter(
            and_(
                Order.status == 'completed',
                Order.created_at >= start_date,
                Order.created_at <= end_date + timedelta(days=1)
            )
        ).group_by(Order.order_type).all()
        
        # Calculate totals
        total_orders = sum(item[1] for item in sales_data)
        total_revenue = sum(float(item[2]) for item in sales_data)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Optional CSV export
        export_format = (request.args.get('format') or '').lower()
        if export_format == 'csv':
            import csv
            from io import StringIO
            csv_buffer = StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow(['Period', 'Order Count', 'Total Revenue', 'Average Order Value'])
            for item in sales_data:
                period_str = (
                    item[0].strftime('%Y-%m-%d') if period == 'daily' else
                    item[0].strftime('%Y-%m') if period == 'monthly' else
                    item[0].strftime('%Y') if period == 'yearly' else
                    item[0].strftime('%Y-%m-%d')
                )
                writer.writerow([period_str, item[1], float(item[2]) if item[2] else 0, float(item[3]) if item[3] else 0])
            # Add summary row
            writer.writerow([])
            writer.writerow(['TOTAL', total_orders, total_revenue, avg_order_value])

            csv_content = csv_buffer.getvalue()
            from flask import make_response
            response = make_response(csv_content)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
            return response

        return jsonify({
            'period': period,
            'startDate': start_date.isoformat(),
            'endDate': end_date.isoformat(),
            'summary': {
                'totalOrders': total_orders,
                'totalRevenue': total_revenue,
                'averageOrderValue': avg_order_value
            },
            'salesData': [
                {
                    'period': item[0].strftime('%Y-%m-%d') if period == 'daily' else 
                             item[0].strftime('%Y-%m-%d') if period == 'weekly' else 
                             item[0].strftime('%Y-%m') if period == 'monthly' else
                             item[0].strftime('%Y'),
                    'orderCount': item[1],
                    'totalRevenue': float(item[2]) if item[2] else 0,
                    'averageOrderValue': float(item[3]) if item[3] else 0
                }
                for item in sales_data
            ],
            'topCustomers': [
                {
                    'customerName': customer[0],
                    'orderCount': customer[1],
                    'totalSpent': float(customer[2]) if customer[2] else 0
                }
                for customer in top_customers
            ],
            'orderTypes': [
                {
                    'type': order_type[0],
                    'count': order_type[1],
                    'revenue': float(order_type[2]) if order_type[2] else 0
                }
                for order_type in order_types
            ]
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to generate sales report'}), 500

@reports_bp.route('/reports/inventory', methods=['GET'])
@jwt_required(optional=True)
def get_inventory_report():
    try:
        # Get inventory summary
        total_items = InventoryItem.query.count()
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.min_stock
        ).count()
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
            func.sum(InventoryItem.current_stock).label('total_stock'),
            func.sum(InventoryItem.current_stock * InventoryItem.cost_per_unit).label('total_value')
        ).group_by(InventoryItem.type).all()
        
        # Get low stock items details
        low_stock_details = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.min_stock
        ).order_by(InventoryItem.current_stock).all()
        
        # Get items by status
        items_by_status = db.session.query(
            InventoryItem.status,
            func.count(InventoryItem.id).label('count')
        ).group_by(InventoryItem.status).all()
        
        return jsonify({
            'summary': {
                'totalItems': total_items,
                'lowStockItems': low_stock_items,
                'outOfStockItems': out_of_stock_items,
                'totalValue': float(total_value)
            },
            'itemsByType': [
                {
                    'type': item[0],
                    'count': item[1],
                    'totalStock': item[2],
                    'totalValue': float(item[3]) if item[3] else 0
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
        return jsonify({'error': 'Failed to generate inventory report'}), 500

@reports_bp.route('/reports/customers', methods=['GET'])
@jwt_required(optional=True)
def get_customers_report():
    try:
        # Get customer summary
        total_customers = Customer.query.count()
        
        # Get customers with orders
        customers_with_orders = db.session.query(func.count(func.distinct(Order.customer_id))).scalar()
        
        # Get top customers by order count
        top_customers_by_orders = db.session.query(
            Order.customer_name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.order_value).label('total_spent'),
            func.avg(Order.order_value).label('avg_order_value')
        ).filter(Order.status == 'completed').group_by(
            Order.customer_name
        ).order_by(func.count(Order.id).desc()).limit(10).all()
        
        # Get top customers by revenue
        top_customers_by_revenue = db.session.query(
            Order.customer_name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.order_value).label('total_spent'),
            func.avg(Order.order_value).label('avg_order_value')
        ).filter(Order.status == 'completed').group_by(
            Order.customer_name
        ).order_by(func.sum(Order.order_value).desc()).limit(10).all()
        
        # Get customer acquisition by month
        customer_acquisition = db.session.query(
            func.date_trunc('month', Customer.created_at).label('month'),
            func.count(Customer.id).label('new_customers')
        ).group_by(
            func.date_trunc('month', Customer.created_at)
        ).order_by('month').all()
        
        return jsonify({
            'summary': {
                'totalCustomers': total_customers,
                'customersWithOrders': customers_with_orders
            },
            'topCustomersByOrders': [
                {
                    'customerName': customer[0],
                    'orderCount': customer[1],
                    'totalSpent': float(customer[2]) if customer[2] else 0,
                    'averageOrderValue': float(customer[3]) if customer[3] else 0
                }
                for customer in top_customers_by_orders
            ],
            'topCustomersByRevenue': [
                {
                    'customerName': customer[0],
                    'orderCount': customer[1],
                    'totalSpent': float(customer[2]) if customer[2] else 0,
                    'averageOrderValue': float(customer[3]) if customer[3] else 0
                }
                for customer in top_customers_by_revenue
            ],
            'customerAcquisition': [
                {
                    'month': acquisition[0].strftime('%Y-%m') if acquisition[0] else None,
                    'newCustomers': acquisition[1]
                }
                for acquisition in customer_acquisition
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate customers report'}), 500

@reports_bp.route('/reports/financial', methods=['GET'])
@jwt_required(optional=True)
def get_financial_report():
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Set default date range if not provided
        if not end_date:
            end_date = date.today()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        # Get revenue from completed orders
        revenue = db.session.query(func.sum(Order.order_value)).filter(
            and_(
                Order.status == 'completed',
                Order.created_at >= start_date,
                Order.created_at <= end_date + timedelta(days=1)
            )
        ).scalar() or 0
        
        # Get invoice statistics
        total_invoices = Invoice.query.filter(
            Invoice.created_at >= start_date,
            Invoice.created_at <= end_date + timedelta(days=1)
        ).count()
        
        paid_invoices = Invoice.query.filter(
            and_(
                Invoice.status == 'paid',
                Invoice.paid_date >= start_date,
                Invoice.paid_date <= end_date
            )
        ).count()
        
        pending_invoices = Invoice.query.filter(
            and_(
                Invoice.status == 'pending',
                Invoice.created_at >= start_date,
                Invoice.created_at <= end_date + timedelta(days=1)
            )
        ).count()
        
        # Get outstanding amount
        outstanding_amount = db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.status == 'pending'
        ).scalar() or 0
        
        # Get collected amount
        collected_amount = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.status == 'paid',
                Invoice.paid_date >= start_date,
                Invoice.paid_date <= end_date
            )
        ).scalar() or 0
        
        # Get monthly revenue trend
        monthly_revenue = db.session.query(
            func.date_trunc('month', Order.created_at).label('month'),
            func.sum(Order.order_value).label('revenue')
        ).filter(
            and_(
                Order.status == 'completed',
                Order.created_at >= start_date - timedelta(days=365),
                Order.created_at <= end_date + timedelta(days=1)
            )
        ).group_by(
            func.date_trunc('month', Order.created_at)
        ).order_by('month').all()
        
        return jsonify({
            'period': {
                'startDate': start_date.isoformat(),
                'endDate': end_date.isoformat()
            },
            'summary': {
                'revenue': float(revenue),
                'totalInvoices': total_invoices,
                'paidInvoices': paid_invoices,
                'pendingInvoices': pending_invoices,
                'outstandingAmount': float(outstanding_amount),
                'collectedAmount': float(collected_amount)
            },
            'monthlyRevenue': [
                {
                    'month': month[0].strftime('%Y-%m') if month[0] else None,
                    'revenue': float(month[1]) if month[1] else 0
                }
                for month in monthly_revenue
            ]
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to generate financial report'}), 500
