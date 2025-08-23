import uuid
from datetime import datetime, timezone

from orm.db_init import session_scope
from orm.models.model_menu import MenuItem


class MenuController:
    def create_menu_item(self, name, size, price, category='General', description=None, image_url=None, is_active=True, sort_order=0):
        with session_scope() as session:
            menu_item_id = str(uuid.uuid4())
            new_menu_item = MenuItem(
                id=menu_item_id,
                name=name,
                size=size,
                price=price,
                category=category,
                description=description,
                image_url=image_url,
                is_active=is_active,
                sort_order=sort_order
            )
            session.add(new_menu_item)
        return self.get_menu_items_by_filters(id=menu_item_id)

    def get_menu_items_by_filters(self, id=None, name=None, size=None, is_active=None, all=False, start_and_end=None):
        with session_scope() as session:
            query = session.query(MenuItem)
            query = query.order_by(MenuItem.name.asc())

            if id:
                query = query.filter(MenuItem.id == id)
            if name:
                query = query.filter(MenuItem.name.ilike(f'%{name}%'))
            if size:
                query = query.filter(MenuItem.size == size)
            if is_active is not None:
                query = query.filter(MenuItem.is_active == is_active)

            if all:
                total = query.count()
                if start_and_end:
                    start, end = start_and_end
                    query = query.slice(start, end)
                menu_items = query.all()
                menu_item_list = [self.menu_item_format(item) for item in menu_items]
                return {'amount': total, 'menu_items': menu_item_list} if menu_item_list else None
            else:
                menu_item = query.first()
                return None if menu_item is None else self.menu_item_format(menu_item)

    def update_menu_item(self, menu_item_id, **fields):
        with session_scope() as session:
            menu_item = session.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
            if not menu_item:
                return None
            for key, value in fields.items():
                if hasattr(menu_item, key) and value is not None:
                    setattr(menu_item, key, value)
            return self.menu_item_format(menu_item)

    def delete_menu_item(self, menu_item_id):
        with session_scope() as session:
            menu_item = session.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
            if not menu_item:
                return False
            session.delete(menu_item)
        return True

    def menu_item_format(self, menu_item):
        return {
            'id': str(menu_item.id),
            'name': menu_item.name,
            'size': menu_item.size,
            'price': float(menu_item.price),
            'category': menu_item.category,
            'description': menu_item.description,
            'imageUrl': menu_item.image_url,
            'isActive': menu_item.is_active,
            'sortOrder': menu_item.sort_order,
            'createdAt': menu_item.created_at.isoformat(),
            'updatedAt': menu_item.updated_at.isoformat()
        }
