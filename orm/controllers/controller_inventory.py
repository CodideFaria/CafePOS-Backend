import uuid
from datetime import datetime, timezone

from orm.db_init import session_scope
from orm.models.model_inventory import InventoryItem


class InventoryController:
    def create_inventory_item(self, name, category, current_stock, min_stock_level=10, unit="pieces"):
        with session_scope() as session:
            inventory_item_id = str(uuid.uuid4())
            new_inventory_item = InventoryItem(
                id=inventory_item_id,
                name=name,
                category=category,
                current_stock=current_stock,
                min_stock_level=min_stock_level,
                unit=unit
            )
            session.add(new_inventory_item)
        return self.get_inventory_items_by_filters(id=inventory_item_id)

    def get_inventory_items_by_filters(self, id=None, name=None, category=None, all=False, start_and_end=None):
        with session_scope() as session:
            query = session.query(InventoryItem)

            if id:
                query = query.filter(InventoryItem.id == id)
            if name:
                query = query.filter(InventoryItem.name.ilike(f'%{name}%'))
            if category:
                query = query.filter(InventoryItem.category == category)

            if all:
                total = query.count()
                if start_and_end:
                    start, end = start_and_end
                    query = query.slice(start, end)
                inventory_items = query.all()
                inventory_item_list = [self.inventory_item_format(item) for item in inventory_items]
                return {'amount': total, 'inventory': inventory_item_list} if inventory_item_list else None
            else:
                inventory_item = query.first()
                return None if inventory_item is None else self.inventory_item_format(inventory_item)

    def update_inventory_item(self, inventory_item_id, **fields):
        with session_scope() as session:
            inventory_item = session.query(InventoryItem).filter(InventoryItem.id == inventory_item_id).first()
            if not inventory_item:
                return None
            for key, value in fields.items():
                if hasattr(inventory_item, key) and value is not None:
                    setattr(inventory_item, key, value)
            return self.inventory_item_format(inventory_item)

    def delete_inventory_item(self, inventory_item_id):
        with session_scope() as session:
            inventory_item = session.query(InventoryItem).filter(InventoryItem.id == inventory_item_id).first()
            if not inventory_item:
                return False
            session.delete(inventory_item)
        return True

    def inventory_item_format(self, inventory_item):
        return {
            'id': str(inventory_item.id),
            'name': inventory_item.name,
            'category': inventory_item.category,
            'currentStock': float(inventory_item.current_stock),
            'minStockLevel': float(inventory_item.min_stock_level),
            'maxStockLevel': float(inventory_item.max_stock_level),
            'unit': inventory_item.unit,
            'costPerUnit': float(inventory_item.cost_per_unit),
            'supplier': inventory_item.supplier,
            'lastRestocked': inventory_item.last_restocked.isoformat() if inventory_item.last_restocked else None,
            'expiryDate': inventory_item.expiry_date.isoformat() if inventory_item.expiry_date else None,
            'barcode': inventory_item.barcode,
            'description': inventory_item.description,
            'location': inventory_item.location,
            'status': inventory_item.status,
            'createdAt': inventory_item.created_at.isoformat(),
            'updatedAt': inventory_item.updated_at.isoformat()
        }
