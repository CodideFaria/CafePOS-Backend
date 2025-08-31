import json
from datetime import datetime, timezone, timedelta
from apis.base_handler import BaseHandler
from orm.controllers.controller_orders import OrderController
from orm.controllers.controller_menu import MenuController
from services.email_service import email_service
from services.scheduler_service import scheduler_service
from orm.db_init import session_scope
from orm.models.model_orders import Order, PaymentMethod, OrderStatus
from orm.models.model_order_items import OrderItem
from orm.models.model_menu import MenuItem
from orm.models.model_users import User
from sqlalchemy import func, and_


class SalesDashboardHandler(BaseHandler):
    def initialize(self):
        self.order_controller = OrderController()

    def get(self):
        # Get query parameters
        start_date = self.get_argument('start_date', None)
        end_date = self.get_argument('end_date', None)
        payment_method = self.get_argument('payment_method', 'all')
        category = self.get_argument('category', None)

        if not start_date or not end_date:
            self.write_error_response(
                ["start_date and end_date parameters are required"], 
                400, 
                "VALIDATION_ERROR"
            )
            return

        try:
            # Get real dashboard data from database
            dashboard_data = self._get_dashboard_data(start_date, end_date, payment_method, category)
            self.write_success(dashboard_data, message="Dashboard data retrieved successfully")

        except Exception as e:
            self.write_error_response([f"Failed to retrieve dashboard data: {str(e)}"], 500, "INTERNAL_ERROR")

    def parse_utc(self, dt_like: str | datetime) -> datetime:
        """Accepts 'YYYY-MM-DD' or full ISO-8601 (with/without Z) and returns aware UTC datetime."""
        if isinstance(dt_like, datetime):
            dt = dt_like
        else:
            s = dt_like.strip()
            # Make 'Z' explicit for fromisoformat; e.g., '...Z' -> '...+00:00'
            if s.endswith('Z'):
                s = s[:-1] + '+00:00'
            try:
                dt = datetime.fromisoformat(s)  # handles 'YYYY-MM-DD' and full ISO
            except ValueError:
                # last resort: date-only
                dt = datetime.strptime(dt_like, '%Y-%m-%d')

        # Ensure timezone-aware UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt

    def ensure_aware_utc(self, dt: datetime | None) -> datetime | None:
        """Return dt as timezone-aware UTC; interpret naive as UTC."""
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _get_dashboard_data(self, start_date, end_date, payment_method='all', category=None):
        """
        Get comprehensive dashboard data from database for date range
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            payment_method (str): Payment method filter ('all', 'cash', 'card')
            category (str): Category filter (optional)
            
        Returns:
            dict: Dashboard data with metrics, charts, and breakdowns
        """
        try:
            # Parse dates
            start_dt = self.parse_utc(start_date)
            end_dt = self.parse_utc(end_date)
            
            with session_scope() as session:
                # Base query for orders in date range
                base_query = session.query(Order).filter(
                    and_(
                        Order.created_at >= start_dt,
                        Order.created_at <= end_dt,
                        Order.status == OrderStatus.completed
                    )
                )
                
                # Apply payment method filter
                if payment_method != 'all':
                    base_query = base_query.filter(Order.payment_method == PaymentMethod(payment_method))
                
                orders = base_query.all()
                
                if not orders:
                    return self._get_empty_dashboard_data()
                
                # Calculate main metrics
                total_revenue = sum(float(order.total_amount) for order in orders)
                total_transactions = len(orders)
                average_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
                
                # Build UTC boundaries once
                now_utc = datetime.now(timezone.utc)
                today_utc = now_utc.date()
                week_ago = now_utc - timedelta(days=7)
                month_ago = now_utc - timedelta(days=30)

                # Safely access created_at (normalize to aware UTC)
                def created_at_utc(o):
                    return self.ensure_aware_utc(o.created_at)

                # Daily
                daily_revenue = 0.0
                daily_transactions = 0
                for o in orders:
                    ca = created_at_utc(o)
                    if ca and ca.date() == today_utc:
                        daily_revenue += float(o.total_amount)
                        daily_transactions += 1

                # Weekly
                weekly_revenue = 0.0
                for o in orders:
                    ca = created_at_utc(o)
                    if ca and ca >= week_ago:
                        weekly_revenue += float(o.total_amount)

                # Monthly
                monthly_revenue = 0.0
                for o in orders:
                    ca = created_at_utc(o)
                    if ca and ca >= month_ago:
                        monthly_revenue += float(o.total_amount)
                
                # Generate chart data (daily aggregates)
                chart_data = self._get_chart_data(session, start_dt, end_dt, payment_method)
                
                # Get top products
                top_products = self._get_top_products(session, start_dt, end_dt, payment_method, category)
                
                # Get category breakdown
                category_breakdown = self._get_category_breakdown(session, start_dt, end_dt, payment_method)
                
                # Get hourly breakdown
                hourly_breakdown = self._get_hourly_breakdown(orders)
                
                # Get comparison data (previous period)
                comparison_data = self._get_comparison_data(session, start_dt, end_dt, payment_method)
                
                return {
                    "metrics": {
                        "totalRevenue": float(total_revenue),
                        "dailyRevenue": float(daily_revenue),
                        "weeklyRevenue": float(weekly_revenue),
                        "monthlyRevenue": float(monthly_revenue),
                        "totalTransactions": total_transactions,
                        "dailyTransactions": daily_transactions,
                        "averageOrderValue": float(average_order_value),
                        "totalCustomers": total_transactions,  # Approximation (could enhance with customer tracking)
                        "returningCustomers": 0,  # Would need customer tracking
                        "newCustomers": total_transactions
                    },
                    "chartData": chart_data,
                    "topProducts": top_products,
                    "categoryBreakdown": category_breakdown,
                    "hourlyBreakdown": hourly_breakdown,
                    "comparisonData": comparison_data
                }
                
        except Exception as e:
            print(f"Error in _get_dashboard_data: {str(e)}")
            # Return empty data structure on error
            return self._get_empty_dashboard_data()
    
    def _get_empty_dashboard_data(self):
        """Return empty but valid dashboard data structure"""
        return {
            "metrics": {
                "totalRevenue": 0.0,
                "dailyRevenue": 0.0,
                "weeklyRevenue": 0.0,
                "monthlyRevenue": 0.0,
                "totalTransactions": 0,
                "dailyTransactions": 0,
                "averageOrderValue": 0.0,
                "totalCustomers": 0,
                "returningCustomers": 0,
                "newCustomers": 0
            },
            "chartData": [],
            "topProducts": [],
            "categoryBreakdown": [],
            "hourlyBreakdown": [],
            "comparisonData": {
                "previousPeriod": {
                    "revenue": 0.0,
                    "transactions": 0,
                    "averageOrderValue": 0.0
                },
                "percentageChange": {
                    "revenue": 0.0,
                    "transactions": 0.0,
                    "averageOrderValue": 0.0
                }
            }
        }
    
    def _get_chart_data(self, session, start_dt, end_dt, payment_method):
        """Generate daily chart data for the date range"""
        try:
            # Group orders by date
            query = session.query(
                func.date(Order.created_at).label('order_date'),
                func.sum(Order.total_amount).label('daily_revenue'),
                func.count(Order.id).label('daily_transactions'),
                func.avg(Order.total_amount).label('avg_order_value')
            ).filter(
                and_(
                    Order.created_at >= start_dt,
                    Order.created_at <= end_dt,
                    Order.status == OrderStatus.completed
                )
            )
            
            if payment_method != 'all':
                query = query.filter(Order.payment_method == PaymentMethod(payment_method))
                
            daily_data = query.group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at)).all()
            
            return [
                {
                    "date": row.order_date.strftime('%Y-%m-%d'),
                    "revenue": float(row.daily_revenue),
                    "transactions": int(row.daily_transactions),
                    "averageOrderValue": float(row.avg_order_value)
                }
                for row in daily_data
            ]
            
        except Exception as e:
            print(f"Error in _get_chart_data: {str(e)}")
            return []
    
    def _get_top_products(self, session, start_dt, end_dt, payment_method, category):
        """Get top selling products for the period"""
        try:
            # Use the exact working query from the fallback that returned 10 products
            query = session.query(
                OrderItem.menu_item_id,
                OrderItem.menu_item_name,
                func.sum(OrderItem.quantity).label('total_quantity'),
                func.sum(OrderItem.unit_price * OrderItem.quantity).label('total_revenue')
            ).select_from(OrderItem).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                and_(
                    Order.created_at >= start_dt,
                    Order.created_at <= end_dt,
                    Order.status == OrderStatus.completed
                )
            )
            
            if payment_method != 'all':
                query = query.filter(Order.payment_method == PaymentMethod(payment_method))

            top_items = query.group_by(
                OrderItem.menu_item_id, OrderItem.menu_item_name
            ).order_by(
                func.sum(OrderItem.quantity).desc()
            ).limit(5).all()
            
            # Look up categories for each product
            results = []
            for item in top_items:
                # Get category from MenuItem table
                menu_item = session.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
                category = menu_item.category if menu_item else "Unknown"
                
                results.append({
                    "id": str(item.menu_item_id),
                    "name": item.menu_item_name,
                    "category": category or "Uncategorized",
                    "quantitySold": int(item.total_quantity),
                    "revenue": float(item.total_revenue),
                    "profitMargin": 65.0
                })
            
            return results
            
        except Exception as e:
            print(f"Error in _get_top_products: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_category_breakdown(self, session, start_dt, end_dt, payment_method):
        """Get revenue breakdown by category"""
        try:
            query = session.query(
                MenuItem.category,
                func.sum(OrderItem.unit_price * OrderItem.quantity).label('category_revenue'),
                func.count(OrderItem.id).label('category_transactions'),
                func.avg(OrderItem.unit_price * OrderItem.quantity).label('avg_order_value')
            ).join(OrderItem).join(Order).filter(
                and_(
                    Order.created_at >= start_dt,
                    Order.created_at <= end_dt,
                    Order.status == OrderStatus.completed
                )
            )
            
            if payment_method != 'all':
                query = query.filter(Order.payment_method == PaymentMethod(payment_method))
                
            category_data = query.group_by(MenuItem.category).all()
            
            # Calculate total revenue for percentage calculation
            total_revenue = sum(float(cat.category_revenue) for cat in category_data)
            
            # Define colors for categories
            category_colors = {
                "Coffee": "#8B4513",
                "Tea": "#228B22",
                "Pastry": "#DAA520",
                "Sandwich": "#CD853F",
                "Beverage": "#4682B4",
                "Dessert": "#FFB6C1"
            }
            
            return [
                {
                    "category": cat.category or "Uncategorized",
                    "revenue": float(cat.category_revenue),
                    "percentage": float(float(cat.category_revenue) / total_revenue * 100) if total_revenue > 0 else 0,
                    "transactions": int(cat.category_transactions),
                    "averageOrderValue": float(cat.avg_order_value),
                    "color": category_colors.get(cat.category, "#999999")
                }
                for cat in category_data
            ]
            
        except Exception as e:
            print(f"Error in _get_category_breakdown: {str(e)}")
            return []
    
    def _get_hourly_breakdown(self, orders):
        """Get revenue breakdown by hour of day (UTC-normalized)."""
        try:
            hourly_data = {}
            for order in orders:
                ca = self.ensure_aware_utc(order.created_at)
                if not ca:
                    continue
                hour = ca.hour
                if hour not in hourly_data:
                    hourly_data[hour] = {"revenue": 0.0, "transactions": 0}
                hourly_data[hour]["revenue"] += float(order.total_amount)
                hourly_data[hour]["transactions"] += 1

            return [
                {"hour": h, "revenue": v["revenue"], "transactions": v["transactions"], "label": f"{h:02d}:00"}
                for h, v in sorted(hourly_data.items())
            ]
        except Exception as e:
            print(f"Error in _get_hourly_breakdown: {str(e)}")
            return []
    
    def _get_comparison_data(self, session, start_dt, end_dt, payment_method):
        """Get comparison data with previous period"""
        try:
            # Calculate previous period dates
            period_length = (end_dt - start_dt).days
            prev_end_dt = start_dt - timedelta(days=1)
            prev_start_dt = prev_end_dt - timedelta(days=period_length)
            
            # Query previous period data
            prev_query = session.query(
                func.sum(Order.total_amount).label('prev_revenue'),
                func.count(Order.id).label('prev_transactions'),
                func.avg(Order.total_amount).label('prev_avg_order_value')
            ).filter(
                and_(
                    Order.created_at >= prev_start_dt,
                    Order.created_at <= prev_end_dt,
                    Order.status == OrderStatus.completed
                )
            )
            
            if payment_method != 'all':
                prev_query = prev_query.filter(Order.payment_method == PaymentMethod(payment_method))
                
            prev_data = prev_query.first()
            
            # Query current period data
            curr_query = session.query(
                func.sum(Order.total_amount).label('curr_revenue'),
                func.count(Order.id).label('curr_transactions'),
                func.avg(Order.total_amount).label('curr_avg_order_value')
            ).filter(
                and_(
                    Order.created_at >= start_dt,
                    Order.created_at <= end_dt,
                    Order.status == OrderStatus.completed
                )
            )
            
            if payment_method != 'all':
                curr_query = curr_query.filter(Order.payment_method == PaymentMethod(payment_method))
                
            curr_data = curr_query.first()
            
            # Calculate percentage changes
            prev_revenue = float(prev_data.prev_revenue or 0)
            curr_revenue = float(curr_data.curr_revenue or 0)
            prev_transactions = int(prev_data.prev_transactions or 0)
            curr_transactions = int(curr_data.curr_transactions or 0)
            prev_avg_order = float(prev_data.prev_avg_order_value or 0)
            curr_avg_order = float(curr_data.curr_avg_order_value or 0)
            
            revenue_change = ((curr_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
            transaction_change = ((curr_transactions - prev_transactions) / prev_transactions * 100) if prev_transactions > 0 else 0
            avg_order_change = ((curr_avg_order - prev_avg_order) / prev_avg_order * 100) if prev_avg_order > 0 else 0
            
            return {
                "previousPeriod": {
                    "revenue": prev_revenue,
                    "transactions": prev_transactions,
                    "averageOrderValue": prev_avg_order
                },
                "percentageChange": {
                    "revenue": round(revenue_change, 1),
                    "transactions": round(transaction_change, 1),
                    "averageOrderValue": round(avg_order_change, 1)
                }
            }
            
        except Exception as e:
            print(f"Error in _get_comparison_data: {str(e)}")
            return {
                "previousPeriod": {"revenue": 0.0, "transactions": 0, "averageOrderValue": 0.0},
                "percentageChange": {"revenue": 0.0, "transactions": 0.0, "averageOrderValue": 0.0}
            }


class DailySalesHandler(BaseHandler):
    def initialize(self):
        self.order_controller = OrderController()

    def get(self):
        # Get query parameter
        date = self.get_argument('date', datetime.now().strftime('%Y-%m-%d'))

        try:
            # Get real daily sales data from database
            sales_data = self.order_controller.get_daily_sales_data(date)
            
            if sales_data is None:
                # Return empty but valid structure if no data
                sales_data = {
                    "date": date,
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
                    "hourlyBreakdown": [],  # Could be implemented with additional query
                    "topSellingItems": [],
                    "staffPerformance": []
                }
            else:
                # Add empty hourly breakdown for now (could be enhanced)
                sales_data["hourlyBreakdown"] = []

            self.write_success(sales_data, message="Daily sales report retrieved successfully")

        except Exception as e:
            self.write_error_response(["Failed to retrieve daily sales report"], 500, "INTERNAL_ERROR")


class EmailDailySummaryHandler(BaseHandler):
    def initialize(self):
        self.order_controller = OrderController()

    def post(self):
        data = self.get_json_body()
        if data is None:
            return

        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        recipients = data.get('recipients', [])
        include_details = data.get('includeDetails', True)

        if not recipients:
            self.write_error_response(
                ["Recipients are required"], 
                400, 
                "VALIDATION_ERROR"
            )
            return

        try:
            # Get real daily sales data from database
            daily_sales_data = self.order_controller.get_daily_sales_data(date)
            
            if daily_sales_data is None:
                # Return empty but valid structure if no data
                daily_sales_data = {
                    "date": date,
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

            # Send email using the email service
            email_result = email_service.send_daily_sales_summary(recipients, daily_sales_data, date)
            
            if email_result['success']:
                response_data = {
                    "emailSent": True,
                    "recipients": recipients,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "mock": email_result.get('mock', False)
                }
                self.write_success(response_data, message="Daily summary email sent successfully")
            else:
                self.write_error_response([email_result['message']], 500, "EMAIL_SEND_ERROR")

        except Exception as e:
            self.write_error_response([f"Failed to send daily summary email: {str(e)}"], 500, "INTERNAL_ERROR")


class TestEmailHandler(BaseHandler):
    """Handler for testing daily email functionality"""
    
    async def post(self):
        """Send a test daily sales email immediately"""
        data = self.get_json_body()
        if data is None:
            return
        
        recipients = data.get('recipients', [])
        
        if not recipients:
            self.write_error_response(
                ["Recipients are required for test email"], 
                400, 
                "VALIDATION_ERROR"
            )
            return
        
        try:
            # Send test email using scheduler service
            result = await scheduler_service.send_test_email(recipients)
            
            if result['success']:
                response_data = {
                    "emailSent": True,
                    "recipients": recipients,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "mock": result.get('mock', False),
                    "testMode": True
                }
                self.write_success(response_data, message="Test email sent successfully")
            else:
                self.write_error_response([result['message']], 500, "EMAIL_TEST_ERROR")
                
        except Exception as e:
            self.write_error_response([f"Failed to send test email: {str(e)}"], 500, "INTERNAL_ERROR")