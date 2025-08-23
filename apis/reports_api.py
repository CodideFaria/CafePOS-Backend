import json
from datetime import datetime, timezone, timedelta
from apis.base_handler import BaseHandler
from orm.controllers.controller_orders import OrderController
from orm.controllers.controller_menu import MenuController


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
            # Mock daily sales data
            mock_data = {
                "date": date,
                "summary": {
                    "totalRevenue": 1250.75,
                    "totalTransactions": 28,
                    "averageOrderValue": 44.67,
                    "taxCollected": 187.61,
                    "discountsGiven": 35.50,
                    "refundsProcessed": 12.00,
                    "paymentMethods": {
                        "cash": 750.25,
                        "card": 500.50
                    }
                },
                "hourlyBreakdown": [
                    {
                        "hour": 8,
                        "revenue": 150.00,
                        "transactions": 3,
                        "averageOrderValue": 50.00
                    },
                    {
                        "hour": 9,
                        "revenue": 200.00,
                        "transactions": 4,
                        "averageOrderValue": 50.00
                    }
                ],
                "topSellingItems": [
                    {
                        "id": "item-uuid-123",
                        "name": "Latte",
                        "quantitySold": 15,
                        "revenue": 225.00
                    }
                ],
                "staffPerformance": [
                    {
                        "userId": "user-uuid-123",
                        "name": "John Cashier",
                        "transactions": 15,
                        "revenue": 675.50,
                        "averageOrderValue": 45.03
                    }
                ]
            }

            self.write_success(mock_data, message="Daily sales report retrieved successfully")

        except Exception as e:
            self.write_error_response(["Failed to retrieve daily sales report"], 500, "INTERNAL_ERROR")


class EmailDailySummaryHandler(BaseHandler):
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
            # In a real implementation, this would send emails
            # For now, simulate email sending
            response_data = {
                "emailSent": True,
                "recipients": recipients,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            self.write_success(response_data, message="Daily summary email sent successfully")

        except Exception as e:
            self.write_error_response(["Failed to send daily summary email"], 500, "INTERNAL_ERROR")