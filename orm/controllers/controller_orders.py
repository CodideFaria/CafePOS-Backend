import uuid
from datetime import datetime, timezone

from orm.db_init import session_scope
from orm.models.model_orders import Order


class OrderController:
    def create_order(self, user_id, subtotal, tax, total, discount_amount=0.0, discount_reason=None, status="PAID"):
        with session_scope() as session:
            order_id = str(uuid.uuid4())
            new_order = Order(
                id=order_id,
                user_id=user_id,
                subtotal=subtotal,
                tax=tax,
                total=total,
                discount_amount=discount_amount,
                discount_reason=discount_reason,
                status=status
            )
            session.add(new_order)
        return self.get_orders_by_filters(id=order_id)

    def get_orders_by_filters(self, id=None, user_id=None, status=None, all=False, start_and_end=None):
        with session_scope() as session:
            query = session.query(Order)
            query = query.order_by(Order.order_time.desc())

            if id:
                query = query.filter(Order.id == id)
            if user_id:
                query = query.filter(Order.user_id == user_id)
            if status:
                query = query.filter(Order.status == status)

            if all:
                total = query.count()
                if start_and_end:
                    start, end = start_and_end
                    query = query.slice(start, end)
                orders = query.all()
                order_list = [self.order_format(order) for order in orders]
                return {'amount': total, 'orders': order_list} if order_list else None
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
        return {
            'id': str(order.id),
            'user_id': str(order.user_id),
            'order_time': order.order_time.isoformat(),
            'subtotal': order.subtotal,
            'tax': order.tax,
            'total': order.total,
            'discount_amount': order.discount_amount,
            'discount_reason': order.discount_reason,
            'status': order.status
        }
