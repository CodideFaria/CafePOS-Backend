import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, and_

from orm.db_init import session_scope
from orm.models.model_orders import Order, PaymentMethod, OrderStatus
from orm.models.model_order_items import OrderItem
from orm.models.model_menu import MenuItem
from orm.models.model_users import User, UserRole


class OrderController:
    def _get_or_create_system_user(self, session):
        """Get or create a system user for orders without valid staff_id"""
        # Try to find an existing admin user
        system_user = session.query(User).filter(User.username == 'admin').first()
        if system_user:
            return str(system_user.id)
        
        # Try to find any admin user
        system_user = session.query(User).filter(User.role == UserRole.admin).first()
        if system_user:
            return str(system_user.id)
            
        # Create a system user if none exists
        system_user_id = str(uuid.uuid4())
        new_user = User(
            id=system_user_id,
            username='system',
            first_name='System',
            last_name='User',
            email='system@cafepos.com',
            role=UserRole.admin,
            password_hash='system',  # Placeholder
            is_active=True
        )
        session.add(new_user)
        return system_user_id
    
    def create_order(self, user_id=None, staff_id=None, subtotal=None, tax=None, tax_amount=None, total=None, total_amount=None, 
                    discount_amount=0.0, discount_reason=None, status="completed", payment_method="cash", 
                    cash_received=0.0, change_given=0.0, amount_paid=None, change_amount=None, 
                    customer_name=None, order_notes=None, items=None, **kwargs):
        with session_scope() as session:
            order_id = str(uuid.uuid4())
            
            # Generate order number (max 20 chars)
            # Format: ORD-YYMMDD-XXXX (4+6+1+4+1 = 16 chars)
            date_str = datetime.now().strftime('%y%m%d')  # Use 2-digit year
            order_suffix = str(order_id).replace('-', '')[:4].upper()  # Remove dashes, take 4 chars
            order_number = f"ORD{date_str}{order_suffix}"  # Total: 3+6+4 = 13 chars
            
            # Handle field name variations
            final_staff_id = staff_id or user_id
            final_tax = tax_amount or tax
            final_total = total_amount or total
            final_change = change_amount or change_given
            final_cash = amount_paid if payment_method == 'cash' else cash_received
            
            # Handle staff_id - if it's not a valid UUID, try to find user or create a default one
            try:
                if final_staff_id:
                    # Try to parse as UUID
                    uuid.UUID(final_staff_id)
                    
                    # Check if user exists
                    existing_user = session.query(User).filter(User.id == final_staff_id).first()
                    if not existing_user:
                        # User doesn't exist, use system user or create one
                        final_staff_id = self._get_or_create_system_user(session)
                else:
                    # No staff_id provided, use system user
                    final_staff_id = self._get_or_create_system_user(session)
            except (ValueError, TypeError):
                # Invalid UUID format, use system user
                final_staff_id = self._get_or_create_system_user(session)
            
            # Handle enum values
            final_payment_method = PaymentMethod(payment_method) if isinstance(payment_method, str) else payment_method
            final_status = OrderStatus(status) if isinstance(status, str) else status
            
            new_order = Order(
                id=order_id,
                order_number=order_number,
                staff_id=final_staff_id,
                subtotal=subtotal,
                tax_amount=final_tax,
                total_amount=final_total,
                discount_amount=discount_amount,
                payment_method=final_payment_method,
                cash_received=final_cash,
                change_amount=final_change,
                status=final_status,
                customer_name=customer_name,
                notes=order_notes
            )
            session.add(new_order)
            
            # Add order items if provided
            if items and isinstance(items, list):
                for item_data in items:
                    # Skip items without valid menu_item_id for now
                    menu_item_id = item_data.get('productId')
                    if not menu_item_id:
                        continue
                        
                    try:
                        quantity = int(item_data.get('quantity', 1))
                        unit_price = float(item_data.get('price', 0))
                        line_total = quantity * unit_price
                        
                        order_item = OrderItem(
                            id=str(uuid.uuid4()),
                            order_id=order_id,
                            menu_item_id=menu_item_id,
                            menu_item_name=item_data.get('productName', 'Unknown Item'),
                            menu_item_size=item_data.get('size', 'Regular'),
                            unit_price=unit_price,
                            quantity=quantity,
                            line_total=line_total,
                            notes=item_data.get('notes', '')
                        )
                        session.add(order_item)
                    except Exception as e:
                        # Skip this item if there's an error
                        print(f"Error adding order item: {e}")
                        continue
                    
        return self.get_orders_by_filters(id=order_id)

    def get_orders_by_filters(self, id=None, user_id=None, status=None, all=False, start_and_end=None):
        with session_scope() as session:
            from sqlalchemy.orm import joinedload
            query = session.query(Order).options(joinedload(Order.order_items))
            query = query.order_by(Order.created_at.desc())

            if id:
                query = query.filter(Order.id == id)
            if user_id:
                query = query.filter(Order.staff_id == user_id)
            if status:
                query = query.filter(Order.status == status)

            if all:
                total = query.count()
                if start_and_end:
                    start, end = start_and_end
                    query = query.slice(start, end)
                orders = query.all()
                order_list = [self.order_format(order) for order in orders]
                return {'amount': total, 'orders': order_list}
            else:
                order = query.first()
                return None if order is None else self.order_format(order)

    def update_order(self, order_id, **fields):
        with session_scope() as session:
            order = session.query(Order).filter(Order.id == order_id).first()
            if not order:
                return None
            for key, value in fields.items():
                if hasattr(order, key) and value is not None:
                    setattr(order, key, value)
            return self.order_format(order)

    def delete_order(self, order_id):
        with session_scope() as session:
            order = session.query(Order).filter(Order.id == order_id).first()
            if not order:
                return False
            session.delete(order)
        return True

    def order_format(self, order):
        # Get order items if they exist
        items = []
        if hasattr(order, 'order_items') and order.order_items:
            items = [{
                'product_id': str(item.menu_item_id) if item.menu_item_id else None,
                'product_name': item.menu_item_name or 'Unknown Item',
                'size': item.menu_item_size or 'Regular',
                'price': float(item.unit_price) if item.unit_price else 0,
                'quantity': item.quantity or 1,
                'notes': item.notes or ''
            } for item in order.order_items]
        
        return {
            'id': str(order.id),
            'order_number': order.order_number,
            'items': items,  # Add items field
            'staff_id': str(order.staff_id) if order.staff_id else None,
            'user_id': str(order.staff_id) if order.staff_id else None,  # For backward compatibility
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'order_time': order.created_at.isoformat() if order.created_at else None,  # For backward compatibility
            'subtotal': float(order.subtotal) if order.subtotal else 0,
            'tax': float(order.tax_amount) if order.tax_amount else 0,
            'tax_amount': float(order.tax_amount) if order.tax_amount else 0,
            'total': float(order.total_amount) if order.total_amount else 0,
            'total_amount': float(order.total_amount) if order.total_amount else 0,
            'discount_amount': float(order.discount_amount) if order.discount_amount else 0,
            'discount_reason': None,  # Field not available in current Order model
            'payment_method': order.payment_method.value if order.payment_method else 'cash',
            'cash_received': float(order.cash_received) if order.cash_received else 0,
            'amount_paid': float(order.cash_received) if order.cash_received else 0,
            'change_given': float(order.change_amount) if order.change_amount else 0,
            'change_amount': float(order.change_amount) if order.change_amount else 0,
            'status': order.status.value if order.status else 'completed',
            'customer_name': order.customer_name,
            'notes': order.notes,
            'reprint_count': order.reprint_count or 0,
            'last_reprint': order.last_reprint.isoformat() if order.last_reprint else None
        }

    def get_daily_sales_data(self, date_str):
        """
        Get comprehensive daily sales data from database
        
        Args:
            date_str (str): Date in YYYY-MM-DD format
            
        Returns:
            dict: Daily sales data with summary, top items, and staff performance
        """
        try:
            # Parse date and create start/end of day timestamps
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_of_day = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
            
            with session_scope() as session:
                # Get orders for the day
                daily_orders = session.query(Order).filter(
                    and_(
                        Order.created_at >= start_of_day,
                        Order.created_at <= end_of_day,
                        Order.status == OrderStatus.completed
                    )
                ).all()

                if not daily_orders:
                    # Return empty but valid structure if no orders
                    return {
                        "date": date_str,
                        "summary": {
                            "totalRevenue": 0.0,
                            "totalTransactions": 0,
                            "averageOrderValue": 0.0,
                            "taxCollected": 0.0,
                            "discountsGiven": 0.0,
                            "refundsProcessed": 0.0,
                            "paymentMethods": {
                                "cash": 0.0,
                                "card": 0.0
                            }
                        },
                        "topSellingItems": [],
                        "staffPerformance": []
                    }

                # Calculate summary metrics
                total_revenue = sum(float(order.total_amount) for order in daily_orders)
                total_transactions = len(daily_orders)
                average_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
                tax_collected = sum(float(order.tax_amount) for order in daily_orders)
                discounts_given = sum(float(order.discount_amount) or 0 for order in daily_orders)

                # Calculate actual payment method breakdown
                cash_revenue = sum(float(order.total_amount) for order in daily_orders if order.payment_method.value == 'cash')
                card_revenue = sum(float(order.total_amount) for order in daily_orders if order.payment_method.value == 'card')

                # Get top selling items
                top_items = session.query(
                    MenuItem.name,
                    MenuItem.id,
                    func.sum(OrderItem.quantity).label('total_quantity'),
                    func.sum(OrderItem.unit_price * OrderItem.quantity).label('total_revenue')
                ).join(OrderItem).join(Order).filter(
                    and_(
                        Order.created_at >= start_of_day,
                        Order.created_at <= end_of_day,
                        Order.status == OrderStatus.completed
                    )
                ).group_by(MenuItem.id, MenuItem.name).order_by(
                    func.sum(OrderItem.quantity).desc()
                ).limit(5).all()

                top_selling_items = [
                    {
                        "id": str(item.id),
                        "name": item.name,
                        "quantitySold": int(item.total_quantity),
                        "revenue": float(item.total_revenue)
                    }
                    for item in top_items
                ]

                # Get staff performance
                staff_performance = session.query(
                    User.id,
                    User.username,
                    func.count(Order.id).label('transaction_count'),
                    func.sum(Order.total_amount).label('total_revenue')
                ).join(Order).filter(
                    and_(
                        Order.created_at >= start_of_day,
                        Order.created_at <= end_of_day,
                        Order.status == OrderStatus.completed
                    )
                ).group_by(User.id, User.username).order_by(
                    func.sum(Order.total_amount).desc()
                ).all()

                staff_performance_data = [
                    {
                        "userId": str(staff.id),
                        "name": staff.username,
                        "transactions": int(staff.transaction_count),
                        "revenue": float(staff.total_revenue),
                        "averageOrderValue": float(staff.total_revenue / staff.transaction_count) if staff.transaction_count > 0 else 0
                    }
                    for staff in staff_performance
                ]

                return {
                    "date": date_str,
                    "summary": {
                        "totalRevenue": float(total_revenue),
                        "totalTransactions": total_transactions,
                        "averageOrderValue": float(average_order_value),
                        "taxCollected": float(tax_collected),
                        "discountsGiven": float(discounts_given),
                        "refundsProcessed": 0.0,  # Would need refund tracking in database
                        "paymentMethods": {
                            "cash": float(cash_revenue),
                            "card": float(card_revenue)
                        }
                    },
                    "topSellingItems": top_selling_items,
                    "staffPerformance": staff_performance_data
                }

        except Exception as e:
            print(f"Error in get_daily_sales_data: {str(e)}")
            return None
