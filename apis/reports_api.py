import json
from datetime import datetime, timezone, timedelta
from apis.base_handler import BaseHandler
from orm.controllers.controller_orders import OrderController
from orm.controllers.controller_menu import MenuController
from services.email_service import email_service
from services.scheduler_service import scheduler_service


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
            # In a real implementation, these would query the database
            # For now, return mock data matching the API specification
            mock_data = {
                "metrics": {
                    "totalRevenue": 15750.50,
                    "dailyRevenue": 850.25,
                    "weeklyRevenue": 5500.75,
                    "monthlyRevenue": 15750.50,
                    "totalTransactions": 245,
                    "dailyTransactions": 18,
                    "averageOrderValue": 64.29,
                    "totalCustomers": 180,
                    "returningCustomers": 108,
                    "newCustomers": 72
                },
                "chartData": [
                    {
                        "date": "2025-01-01",
                        "revenue": 800.50,
                        "transactions": 15,
                        "averageOrderValue": 53.37
                    }
                ],
                "topProducts": [
                    {
                        "id": "item-uuid-123",
                        "name": "Latte",
                        "category": "Coffee",
                        "quantitySold": 45,
                        "revenue": 202.50,
                        "profitMargin": 65.0
                    }
                ],
                "categoryBreakdown": [
                    {
                        "category": "Coffee",
                        "revenue": 10000.00,
                        "percentage": 63.5,
                        "transactions": 150,
                        "averageOrderValue": 66.67,
                        "color": "#8B4513"
                    }
                ],
                "hourlyBreakdown": [
                    {
                        "hour": 8,
                        "revenue": 450.00,
                        "transactions": 8,
                        "label": "08:00"
                    }
                ],
                "comparisonData": {
                    "previousPeriod": {
                        "revenue": 14250.00,
                        "transactions": 220,
                        "averageOrderValue": 64.77
                    },
                    "percentageChange": {
                        "revenue": 10.5,
                        "transactions": 11.4,
                        "averageOrderValue": -0.7
                    }
                }
            }

            self.write_success(mock_data, message="Dashboard data retrieved successfully")

        except Exception as e:
            self.write_error_response(["Failed to retrieve dashboard data"], 500, "INTERNAL_ERROR")


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