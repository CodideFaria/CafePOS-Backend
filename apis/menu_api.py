import json
import os
from decouple import config
from apis.base_handler import BaseHandler
from orm.controllers.controller_menu import MenuController

UPLOAD_DIR = config('UPLOAD_DIR', default='uploads')

class MenuItemsHandler(BaseHandler):
    def initialize(self):
        self.menu_controller = MenuController()
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

    def get(self):
        menu_items = self.menu_controller.get_menu_items_by_filters(all=True)
        if menu_items:
            self.write_success(menu_items)
        else:
            self.write_success({"menu_items": [], "amount": 0})

    def post(self):
        # Handle both JSON and form data
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            data = self.get_json_body()
            if data is None:
                return
            
            name = data.get('name')
            size = data.get('size')
            price = data.get('price')
            category = data.get('category')
            description = data.get('description')
            image_url = data.get('imageUrl')
            is_active = data.get('isActive', True)
            sort_order = data.get('sortOrder', 0)
        else:
            # Form data handling
            name = self.get_body_argument('name', None)
            size = self.get_body_argument('size', None)
            try:
                price = float(self.get_body_argument('price')) if self.get_body_argument('price', None) else None
            except (ValueError, TypeError):
                price = None
            category = self.get_body_argument('category', 'General')
            description = self.get_body_argument('description', None)
            image_url = None
            is_active = self.get_body_argument('isActive', 'true').lower() == 'true'
            sort_order = int(self.get_body_argument('sortOrder', '0'))
        
        # Validation
        errors = []
        if not name or len(name.strip()) == 0:
            errors.append("Name is required")
        elif len(name) > 100:
            errors.append("Name must be 100 characters or less")
            
        if not size or len(size.strip()) == 0:
            errors.append("Size is required")
        elif len(size) > 50:
            errors.append("Size must be 50 characters or less")
            
        if price is None or price <= 0:
            errors.append("Price must be a positive number")
        elif price > 9999.99:
            errors.append("Price cannot exceed 9999.99")
            
        if errors:
            self.write_error_response(errors, 422, "VALIDATION_ERROR")
            return

        # Handle file upload if present
        if self.request.files and 'image' in self.request.files:
            file_info = self.request.files['image'][0]
            filename = file_info['filename']
            image_path = os.path.join(UPLOAD_DIR, filename)
            with open(image_path, 'wb') as f:
                f.write(file_info['body'])
            image_url = image_path

        try:
            new_menu_item = self.menu_controller.create_menu_item(
                name=name.strip(),
                size=size.strip(),
                price=price,
                category=category,
                description=description,
                image_url=image_url,
                is_active=is_active,
                sort_order=sort_order
            )
            self.write_success(new_menu_item, 201)
        except Exception as e:
            self.write_error_response(["Failed to create menu item"], 500, "INTERNAL_ERROR")


class MenuItemHandler(BaseHandler):
    def initialize(self):
        self.menu_controller = MenuController()
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

    def get(self, id):
        try:
            menu_item = self.menu_controller.get_menu_items_by_filters(id=id)
            if menu_item:
                self.write_success(menu_item)
            else:
                self.write_error_response(["Menu item not found"], 404, "NOT_FOUND")
        except Exception as e:
            self.write_error_response(["Failed to retrieve menu item"], 500, "INTERNAL_ERROR")

    def put(self, id):
        # Handle both JSON and form data
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            data = self.get_json_body()
            if data is None:
                return
        else:
            # Form data handling
            data = {}
            for key in self.request.body_arguments:
                data[key] = self.get_body_argument(key)
        
        # Validate and convert data types
        update_data = {}
        errors = []
        
        if 'name' in data:
            name = data['name']
            if not name or len(name.strip()) == 0:
                errors.append("Name cannot be empty")
            elif len(name) > 100:
                errors.append("Name must be 100 characters or less")
            else:
                update_data['name'] = name.strip()
                
        if 'size' in data:
            size = data['size']
            if not size or len(size.strip()) == 0:
                errors.append("Size cannot be empty")
            elif len(size) > 50:
                errors.append("Size must be 50 characters or less")
            else:
                update_data['size'] = size.strip()
                
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    errors.append("Price must be a positive number")
                elif price > 9999.99:
                    errors.append("Price cannot exceed 9999.99")
                else:
                    update_data['price'] = price
            except (ValueError, TypeError):
                errors.append("Price must be a valid number")
                
        for field in ['category', 'description', 'imageUrl', 'isActive', 'sortOrder']:
            if field in data:
                if field == 'isActive':
                    update_data['is_active'] = bool(data[field]) if isinstance(data[field], bool) else str(data[field]).lower() == 'true'
                elif field == 'sortOrder':
                    try:
                        update_data['sort_order'] = int(data[field])
                    except (ValueError, TypeError):
                        errors.append("Sort order must be a valid integer")
                elif field == 'imageUrl':
                    update_data['image_url'] = data[field]
                else:
                    update_data[field] = data[field]

        # Handle file upload if present
        if self.request.files and 'image' in self.request.files:
            file_info = self.request.files['image'][0]
            filename = file_info['filename']
            image_path = os.path.join(UPLOAD_DIR, filename)
            with open(image_path, 'wb') as f:
                f.write(file_info['body'])
            update_data['image_url'] = image_path
            
        if errors:
            self.write_error_response(errors, 422, "VALIDATION_ERROR")
            return

        try:
            updated_menu_item = self.menu_controller.update_menu_item(id, **update_data)
            if updated_menu_item:
                self.write_success(updated_menu_item)
            else:
                self.write_error_response(["Menu item not found"], 404, "NOT_FOUND")
        except Exception as e:
            self.write_error_response(["Failed to update menu item"], 500, "INTERNAL_ERROR")

    def delete(self, id):
        try:
            if self.menu_controller.delete_menu_item(id):
                self.set_status(204)
                self.finish()
            else:
                self.write_error_response(["Menu item not found"], 404, "NOT_FOUND")
        except Exception as e:
            self.write_error_response(["Failed to delete menu item"], 500, "INTERNAL_ERROR")


class MenuItemsBulkImportHandler(BaseHandler):
    def initialize(self):
        self.menu_controller = MenuController()

    def post(self):
        # Check if file was uploaded
        if not self.request.files or 'file' not in self.request.files:
            self.write_error_response(["CSV file is required"], 400, "VALIDATION_ERROR")
            return

        # Get form parameters
        skip_duplicates = self.get_body_argument('skipDuplicates', 'true').lower() == 'true'
        update_existing = self.get_body_argument('updateExisting', 'false').lower() == 'true'

        try:
            file_info = self.request.files['file'][0]
            csv_content = file_info['body'].decode('utf-8')
            
            # Parse CSV
            import csv
            import io
            
            reader = csv.DictReader(io.StringIO(csv_content))
            
            imported = 0
            skipped = 0
            errors = 0
            error_details = []
            
            for row_num, row in enumerate(reader, 1):
                try:
                    name = row.get('name', '').strip()
                    description = row.get('description', '').strip()
                    category = row.get('category', 'General').strip()
                    size_name = row.get('size_name', 'Regular').strip()
                    size_price = float(row.get('size_price', 0))
                    size_volume = row.get('size_volume', '').strip()
                    allergens = row.get('allergens', '').strip()
                    calories = int(row.get('calories', 0)) if row.get('calories') else 0

                    if not name or size_price <= 0:
                        error_details.append({
                            "row": row_num,
                            "error": "Name and valid price are required",
                            "data": ','.join(row.values())
                        })
                        errors += 1
                        continue

                    # Check for existing item
                    existing_item = None
                    if skip_duplicates or update_existing:
                        # Look for existing item by name and size
                        existing_items = self.menu_controller.get_menu_items_by_filters(all=True)
                        if existing_items and 'menu_items' in existing_items:
                            existing_item = next((
                                item for item in existing_items['menu_items'] 
                                if item['name'].lower() == name.lower() and item['size'].lower() == size_name.lower()
                            ), None)
                    
                    if existing_item:
                        if update_existing:
                            # Update existing item
                            update_data = {
                                'description': description,
                                'category': category,
                                'price': size_price,
                                'calories': calories
                            }
                            if allergens:
                                update_data['allergens'] = allergens
                            if size_volume:
                                update_data['size_volume'] = size_volume
                                
                            updated_item = self.menu_controller.update_menu_item(existing_item['id'], **update_data)
                            if updated_item:
                                imported += 1
                            else:
                                error_details.append({
                                    "row": row_num,
                                    "error": "Failed to update existing item",
                                    "data": f"{name} - {size_name}"
                                })
                                errors += 1
                        else:
                            # Skip duplicate
                            skipped += 1
                    else:
                        # Create new item
                        try:
                            new_item = self.menu_controller.create_menu_item(
                                name=name,
                                size=size_name,
                                price=size_price,
                                description=description,
                                category=category,
                                calories=calories,
                                allergens=allergens if allergens else None,
                                size_volume=size_volume if size_volume else None,
                                is_active=True,
                                sort_order=0
                            )
                            if new_item:
                                imported += 1
                            else:
                                error_details.append({
                                    "row": row_num,
                                    "error": "Failed to create menu item",
                                    "data": f"{name} - {size_name}"
                                })
                                errors += 1
                        except Exception as create_error:
                            error_details.append({
                                "row": row_num,
                                "error": f"Creation error: {str(create_error)}",
                                "data": f"{name} - {size_name}"
                            })
                            errors += 1

                except Exception as e:
                    error_details.append({
                        "row": row_num,
                        "error": str(e),
                        "data": ','.join(row.values()) if row else ""
                    })
                    errors += 1

            response_data = {
                "imported": imported,
                "skipped": skipped,
                "errors": errors,
                "details": error_details
            }

            self.write_success(response_data, message="Bulk import completed")

        except Exception as e:
            self.write_error_response(["Failed to process bulk import"], 500, "INTERNAL_ERROR")
