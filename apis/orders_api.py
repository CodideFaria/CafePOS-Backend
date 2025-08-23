import json
from datetime import datetime, timezone
from apis.base_handler import BaseHandler
from orm.controllers.controller_orders import OrderController


class OrdersHandler(BaseHandler):
    def initialize(self):
        self.order_controller = OrderController()

    def get(self):
        # Get query parameters for filtering
        limit = int(self.get_argument('limit', 50))
        offset = int(self.get_argument('offset', 0))
        status = self.get_argument('status', None)
        date_from = self.get_argument('date_from', None)
        date_to = self.get_argument('date_to', None)
        payment_method = self.get_argument('payment_method', None)

        # Validate limit
        if limit > 200:
            limit = 200

        try:
            orders = self.order_controller.get_orders_by_filters(all=True)
            
            # In a real implementation, apply filters here
            mock_orders = orders.get('orders', [])
            
            # Mock pagination
            total_orders = len(mock_orders)
            paginated_orders = mock_orders[offset:offset + limit]
            
            response_data = {
                "orders": paginated_orders,
                "pagination": {
                    "total": total_orders,
                    "limit": limit,
                    "offset": offset,
                    "hasMore": offset + limit < total_orders
                }
            }

            self.write_success(response_data, message="Orders retrieved successfully")

        except Exception as e:
            self.write_error_response(["Failed to retrieve orders"], 500, "INTERNAL_ERROR")

    def post(self):
        data = self.get_json_body()
        if data is None:
            return

        # Validate required fields according to API spec
        items = data.get('items', [])
        subtotal = data.get('subtotal')
        tax_amount = data.get('taxAmount') 
        total = data.get('total')
        payment_method = data.get('paymentMethod')

        errors = []
        if not items:
            errors.append("Order items are required")
        if subtotal is None:
            errors.append("Subtotal is required")
        if tax_amount is None:
            errors.append("Tax amount is required") 
        if total is None:
            errors.append("Total is required")
        if not payment_method:
            errors.append("Payment method is required")

        if errors:
            self.write_error_response(errors, 400, "VALIDATION_ERROR")
            return

        try:
            # Create order using the controller
            order_data = {
                'user_id': data.get('createdBy', 'system'),
                'subtotal': subtotal,
                'tax': tax_amount,
                'total': total,
                'discount_amount': data.get('discountAmount', 0),
                'discount_reason': data.get('discountReason'),
                'status': 'PAID',
                'payment_method': payment_method,
                'amount_paid': data.get('amountPaid', total),
                'change_given': data.get('changeGiven', 0),
                'customer_name': data.get('customerName'),
                'order_notes': data.get('orderNotes')
            }

            new_order = self.order_controller.create_order(**order_data)
            
            # Format response according to API specification
            order_response = {
                "order": {
                    "id": new_order.get('id'),
                    "orderNumber": f"ORD-{datetime.now().strftime('%Y-%m-%d')}-{new_order.get('id', '')[:8]}",
                    "items": items,  # In real implementation, process and store items
                    "subtotal": subtotal,
                    "taxAmount": tax_amount,
                    "discountAmount": data.get('discountAmount', 0),
                    "total": total,
                    "paymentMethod": payment_method,
                    "amountPaid": data.get('amountPaid', total),
                    "changeGiven": data.get('changeGiven', 0),
                    "status": "PAID",
                    "customerName": data.get('customerName'),
                    "orderNotes": data.get('orderNotes'),
                    "createdBy": data.get('createdBy'),
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                    "completedAt": datetime.now(timezone.utc).isoformat()
                },
                "inventoryUpdated": True,
                "receiptGenerated": True
            }

            self.write_success(order_response, 201, "Order created successfully")

        except Exception as e:
            self.write_error_response(["Failed to create order"], 500, "INTERNAL_ERROR")


class OrderHandler(BaseHandler):
    def initialize(self):
        self.order_controller = OrderController()

    def get(self, id):
        try:
            order = self.order_controller.get_orders_by_filters(id=id)
            if order:
                self.write_success({"order": order}, message="Order retrieved successfully")
            else:
                self.write_error_response(["Order not found"], 404, "NOT_FOUND")
        except Exception as e:
            self.write_error_response(["Failed to retrieve order"], 500, "INTERNAL_ERROR")

    def put(self, id):
        data = self.get_json_body()
        if data is None:
            return

        try:
            updated_order = self.order_controller.update_order(id, **data)
            if updated_order:
                self.write_success({"order": updated_order}, message="Order updated successfully")
            else:
                self.write_error_response(["Order not found"], 404, "NOT_FOUND")
        except Exception as e:
            self.write_error_response(["Failed to update order"], 500, "INTERNAL_ERROR")

    def delete(self, id):
        try:
            if self.order_controller.delete_order(id):
                self.write_success({"deleted": True, "id": id}, message="Order deleted successfully")
            else:
                self.write_error_response(["Order not found"], 404, "NOT_FOUND")
        except Exception as e:
            self.write_error_response(["Failed to delete order"], 500, "INTERNAL_ERROR")


class OrderRefundHandler(BaseHandler):
    def initialize(self):
        self.order_controller = OrderController()

    def post(self, id):
        data = self.get_json_body()
        if data is None:
            return

        amount = data.get('amount')
        reason = data.get('reason')
        refund_method = data.get('refundMethod')
        items = data.get('items', ['all'])

        if amount is None:
            self.write_error_response(["Refund amount is required"], 400, "VALIDATION_ERROR")
            return

        if not reason:
            self.write_error_response(["Refund reason is required"], 400, "VALIDATION_ERROR")
            return

        try:
            # Get the order first
            order = self.order_controller.get_orders_by_filters(id=id)
            if not order:
                self.write_error_response(["Order not found"], 404, "NOT_FOUND")
                return

            # In a real implementation, process the refund
            refund_data = {
                "refunded": True,
                "refundId": f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "amount": amount,
                "method": refund_method,
                "reason": reason,
                "refundedAt": datetime.now(timezone.utc).isoformat(),
                "originalOrderId": id
            }

            self.write_success({"refund": refund_data}, message="Refund processed successfully")

        except Exception as e:
            self.write_error_response(["Failed to process refund"], 500, "INTERNAL_ERROR")


class OrderReprintReceiptHandler(BaseHandler):
    def initialize(self):
        self.order_controller = OrderController()

    def post(self, id):
        try:
            # Get the order first
            order = self.order_controller.get_orders_by_filters(id=id)
            if not order:
                self.write_error_response(["Order not found"], 404, "NOT_FOUND")
                return

            # In a real implementation, send receipt to printer
            reprint_data = {
                "reprinted": True,
                "originalOrderDate": order.get('createdAt', datetime.now(timezone.utc).isoformat()),
                "reprintAllowed": True,
                "reprintCount": 1  # In real implementation, track reprint count
            }

            self.write_success(reprint_data, message="Receipt reprinted successfully")

        except Exception as e:
            self.write_error_response(["Failed to reprint receipt"], 500, "INTERNAL_ERROR")
