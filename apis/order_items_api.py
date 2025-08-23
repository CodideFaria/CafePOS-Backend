import json
from apis.base_handler import BaseHandler
from orm.controllers.controller_order_items import OrderItemController


class OrderItemsHandler(BaseHandler):
    def initialize(self):
        self.order_item_controller = OrderItemController()

    def get(self):
        order_items = self.order_item_controller.get_order_items_by_filters(all=True)
        self.write(json.dumps(order_items))

    def post(self):
        data = json.loads(self.request.body)
        order_id = data.get('order_id')
        menu_item_id = data.get('menu_item_id')
        quantity = data.get('quantity')
        price_at_time_of_sale = data.get('price_at_time_of_sale')

        if not order_id or not menu_item_id or quantity is None or price_at_time_of_sale is None:
            self.set_status(400)
            self.write({"error": "Missing required order item data"})
            return

        new_order_item = self.order_item_controller.create_order_item(order_id, menu_item_id, quantity, price_at_time_of_sale)
        self.set_status(201)
        self.write(json.dumps(new_order_item))


class OrderItemHandler(BaseHandler):
    def initialize(self):
        self.order_item_controller = OrderItemController()

    def get(self, id):
        order_item = self.order_item_controller.get_order_items_by_filters(id=id)
        if order_item:
            self.write(json.dumps(order_item))
        else:
            self.set_status(404)
            self.write({"error": "Order item not found"})

    def put(self, id):
        data = json.loads(self.request.body)
        updated_order_item = self.order_item_controller.update_order_item(id, **data)
        if updated_order_item:
            self.write(json.dumps(updated_order_item))
        else:
            self.set_status(404)
            self.write({"error": "Order item not found"})

    def delete(self, id):
        if self.order_item_controller.delete_order_item(id):
            self.set_status(204)
        else:
            self.set_status(404)
            self.write({"error": "Order item not found"})
