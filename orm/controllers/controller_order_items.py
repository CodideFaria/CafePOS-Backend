import uuid

from orm.db_init import session_scope
from orm.models.model_order_items import OrderItem


class OrderItemController:
    def create_order_item(self, order_id, menu_item_id, quantity, price_at_time_of_sale):
        with session_scope() as session:
            order_item_id = str(uuid.uuid4())
            new_order_item = OrderItem(
                id=order_item_id,
                order_id=order_id,
                menu_item_id=menu_item_id,
                quantity=quantity,
                price_at_time_of_sale=price_at_time_of_sale
            )
            session.add(new_order_item)
        return self.get_order_items_by_filters(id=order_item_id)

    def get_order_items_by_filters(self, id=None, order_id=None, menu_item_id=None, all=False, start_and_end=None):
        with session_scope() as session:
            query = session.query(OrderItem)

            if id:
                query = query.filter(OrderItem.id == id)
            if order_id:
                query = query.filter(OrderItem.order_id == order_id)
            if menu_item_id:
                query = query.filter(OrderItem.menu_item_id == menu_item_id)

            if all:
                total = query.count()
                if start_and_end:
                    start, end = start_and_end
                    query = query.slice(start, end)
                order_items = query.all()
                order_item_list = [self.order_item_format(item) for item in order_items]
                return {'amount': total, 'order_items': order_item_list} if order_item_list else None
            else:
                order_item = query.first()
                return None if order_item is None else self.order_item_format(order_item)

    def update_order_item(self, order_item_id, **fields):
        with session_scope() as session:
            order_item = session.query(OrderItem).filter(OrderItem.id == order_item_id).first()
            if not order_item:
                return None
            for key, value in fields.items():
                if hasattr(order_item, key) and value is not None:
                    setattr(order_item, key, value)
            return self.order_item_format(order_item)

    def delete_order_item(self, order_item_id):
        with session_scope() as session:
            order_item = session.query(OrderItem).filter(OrderItem.id == order_item_id).first()
            if not order_item:
                return False
            session.delete(order_item)
        return True

    def order_item_format(self, order_item):
        return {
            'id': str(order_item.id),
            'order_id': str(order_item.order_id),
            'menu_item_id': str(order_item.menu_item_id),
            'quantity': order_item.quantity,
            'price_at_time_of_sale': order_item.price_at_time_of_sale
        }
