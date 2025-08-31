import json
import csv
import io
from datetime import datetime, timezone
from apis.base_handler import BaseHandler
from orm.controllers.controller_inventory import InventoryController


class InventoryItemsHandler(BaseHandler):
    def initialize(self):
        self.inventory_controller = InventoryController()

    def get(self):
        try:
            inventory_items = self.inventory_controller.get_inventory_items_by_filters(all=True)
            inventory_items = inventory_items or {"inventory": []}
            
            # Format response according to API specification
            response_data = {
                "inventory": inventory_items.get('inventory', []),
                "lowStockItems": sum(1 for item in inventory_items.get('inventory', []) if item.get('isLowStock')),
                "totalItems": len(inventory_items.get('inventory', []))
            }
            
            self.write_success(response_data, message="Inventory retrieved successfully")
        except Exception as e:
            self.write_error_response(["Failed to retrieve inventory"], 500, "INTERNAL_ERROR")

    def post(self):
        data = self.get_json_body()
        if data is None:
            return

        menu_item_id = data.get('menu_item_id')
        quantity = data.get('quantity')
        low_stock_threshold = data.get('low_stock_threshold')

        if not menu_item_id or quantity is None:
            self.write_error_response(["Menu item ID and quantity are required"], 400, "VALIDATION_ERROR")
            return

        try:
            new_inventory_item = self.inventory_controller.create_inventory_item(menu_item_id, quantity, low_stock_threshold)
            self.write_success({"inventory_item": new_inventory_item}, 201, "Inventory item created successfully")
        except Exception as e:
            self.write_error_response(["Failed to create inventory item"], 500, "INTERNAL_ERROR")


class InventoryItemHandler(BaseHandler):
    def initialize(self):
        self.inventory_controller = InventoryController()

    def get(self, id):
        try:
            inventory_item = self.inventory_controller.get_inventory_items_by_filters(id=id)
            if inventory_item:
                self.write_success({"inventory_item": inventory_item}, message="Inventory item retrieved successfully")
            else:
                self.write_error_response(["Inventory item not found"], 404, "NOT_FOUND")
        except Exception as e:
            self.write_error_response(["Failed to retrieve inventory item"], 500, "INTERNAL_ERROR")

    def put(self, id):
        data = self.get_json_body()
        if data is None:
            return

        try:
            updated_inventory_item = self.inventory_controller.update_inventory_item(id, **data)
            if updated_inventory_item:
                self.write_success({"inventory_item": updated_inventory_item}, message="Inventory item updated successfully")
            else:
                self.write_error_response(["Inventory item not found"], 404, "NOT_FOUND")
        except Exception as e:
            self.write_error_response(["Failed to update inventory item"], 500, "INTERNAL_ERROR")

    def delete(self, id):
        try:
            if self.inventory_controller.delete_inventory_item(id):
                self.write_success({"deleted": True, "id": id}, message="Inventory item deleted successfully")
            else:
                self.write_error_response(["Inventory item not found"], 404, "NOT_FOUND")
        except Exception as e:
            self.write_error_response(["Failed to delete inventory item"], 500, "INTERNAL_ERROR")


class InventoryAdjustHandler(BaseHandler):
    def initialize(self):
        self.inventory_controller = InventoryController()

    def post(self, id):
        data = self.get_json_body()
        if data is None:
            return

        adjustment = data.get('adjustment')
        reason = data.get('reason', 'ADJUSTMENT')
        notes = data.get('notes', '')
        reference = data.get('reference', '')

        if adjustment is None:
            self.write_error_response(["Adjustment amount is required"], 400, "VALIDATION_ERROR")
            return

        if reason not in ['RESTOCK', 'SALE', 'WASTE', 'ADJUSTMENT']:
            self.write_error_response(["Invalid reason. Must be one of: RESTOCK, SALE, WASTE, ADJUSTMENT"], 400, "VALIDATION_ERROR")
            return

        try:
            # Get current inventory item
            current_item = self.inventory_controller.get_inventory_items_by_filters(id=id)
            if not current_item:
                self.write_error_response(["Inventory item not found"], 404, "NOT_FOUND")
                return

            previous_stock = current_item.get('currentStock', 0)
            new_stock = previous_stock + adjustment

            if new_stock < 0:
                self.write_error_response(["Adjustment would result in negative stock"], 400, "INVALID_ADJUSTMENT")
                return

            # Update inventory
            updated_inventory = self.inventory_controller.update_inventory_item(id, currentStock=new_stock)
            
            # Create adjustment record (would be stored in database in real implementation)
            adjustment_record = {
                "id": f"adj-{datetime.now(timezone.utc).isoformat()}",
                "previousStock": previous_stock,
                "newStock": new_stock,
                "adjustment": adjustment,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "notes": notes,
                "reference": reference
            }

            response_data = {
                "inventory": updated_inventory,
                "adjustment": adjustment_record
            }

            self.write_success(response_data, message="Stock adjusted successfully")

        except Exception as e:
            self.write_error_response(["Failed to adjust stock"], 500, "INTERNAL_ERROR")


class InventoryExportHandler(BaseHandler):
    def initialize(self):
        self.inventory_controller = InventoryController()

    def get(self):
        try:
            inventory_items = self.inventory_controller.get_inventory_items_by_filters(all=True)
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Item ID', 'Name', 'Current Stock', 'Minimum Stock', 
                'Cost Per Unit', 'Last Updated'
            ])
            
            # Write data rows
            for item in inventory_items.get('inventory', []):
                writer.writerow([
                    item.get('id', ''),
                    item.get('menuItemName', ''),
                    item.get('currentStock', 0),
                    item.get('minimumStock', 0),
                    item.get('costPerUnit', 0),
                    item.get('updatedAt', '')
                ])

            # Set headers for CSV download
            filename = f"inventory-export-{datetime.now().strftime('%Y%m%d')}.csv"
            self.set_header('Content-Type', 'text/csv')
            self.set_header('Content-Disposition', f'attachment; filename="{filename}"')
            
            self.write(output.getvalue())

        except Exception as e:
            self.write_error_response(["Failed to export inventory"], 500, "INTERNAL_ERROR")
