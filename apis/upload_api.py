import os
import uuid
import mimetypes
from PIL import Image
import tornado.web
from decouple import config
from apis.base_handler import BaseHandler
from orm.controllers.controller_menu import MenuController

class ImageUploadHandler(BaseHandler):
    """Handle image uploads for menu items"""
    
    def initialize(self):
        self.menu_controller = MenuController()
        self.upload_dir = config('UPLOAD_DIR', default='uploads')
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, 'menu_items'), exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, 'thumbnails'), exist_ok=True)
    
    async def post(self):
        """Upload image for a menu item"""
        try:
            # Get menu item ID
            menu_item_id = self.get_argument('menu_item_id', None)
            if not menu_item_id:
                self.write_error_response(
                    ["menu_item_id is required"], 
                    400, 
                    "VALIDATION_ERROR"
                )
                return
            
            # Check if menu item exists  
            menu_item = self.menu_controller.get_menu_items_by_filters(id=menu_item_id)
            
            if not menu_item:
                self.write_error_response(
                    ["Menu item not found"], 
                    404, 
                    "NOT_FOUND"
                )
                return
            
            # Get uploaded file
            if 'image' not in self.request.files:
                self.write_error_response(
                    ["No image file provided"], 
                    400, 
                    "VALIDATION_ERROR"
                )
                return
            
            file_info = self.request.files['image'][0]
            filename = file_info['filename']
            file_body = file_info['body']
            
            # Validate file size
            if len(file_body) > self.max_file_size:
                self.write_error_response(
                    ["File size too large. Maximum 10MB allowed."], 
                    400, 
                    "FILE_TOO_LARGE"
                )
                return
            
            # Validate file extension
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in self.allowed_extensions:
                self.write_error_response(
                    [f"Invalid file type. Allowed: {', '.join(self.allowed_extensions)}"], 
                    400, 
                    "INVALID_FILE_TYPE"
                )
                return
            
            # Generate unique filename
            unique_filename = f"{menu_item_id}_{uuid.uuid4().hex[:8]}{file_ext}"
            file_path = os.path.join(self.upload_dir, 'menu_items', unique_filename)
            
            # Save original image
            with open(file_path, 'wb') as f:
                f.write(file_body)
            
            # Create thumbnail
            thumbnail_path = self._create_thumbnail(file_path, unique_filename)
            
            # Update menu item with image URL
            image_url = f"/uploads/menu_items/{unique_filename}"
            thumbnail_url = f"/uploads/thumbnails/{unique_filename}" if thumbnail_path else None
            
            updated_item = self.menu_controller.update_menu_item(
                menu_item_id, 
                image_url=image_url
            )
            
            if updated_item:
                response_data = {
                    "menu_item_id": menu_item_id,
                    "filename": unique_filename,
                    "original_filename": filename,
                    "image_url": image_url,
                    "thumbnail_url": thumbnail_url,
                    "file_size": len(file_body),
                    "menu_item": {
                        "id": updated_item['id'],
                        "name": updated_item['name'],
                        "size": updated_item['size'],
                        "imageUrl": updated_item['imageUrl']
                    }
                }
                self.write_success(response_data, message="Image uploaded successfully")
            else:
                # Clean up uploaded file if database update failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                if thumbnail_path and os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                
                self.write_error_response(
                    ["Failed to update menu item with image"], 
                    500, 
                    "DATABASE_ERROR"
                )
                
        except Exception as e:
            self.write_error_response(
                [f"Upload failed: {str(e)}"], 
                500, 
                "UPLOAD_ERROR"
            )
    
    def _create_thumbnail(self, original_path, filename):
        """Create thumbnail version of uploaded image"""
        try:
            thumbnail_filename = filename
            thumbnail_path = os.path.join(self.upload_dir, 'thumbnails', thumbnail_filename)
            
            with Image.open(original_path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail (300x300 max, maintaining aspect ratio)
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
                
            return thumbnail_path
        except Exception as e:
            print(f"Failed to create thumbnail: {str(e)}")
            return None


class ImageServeHandler(tornado.web.StaticFileHandler):
    """Serve uploaded images with proper headers"""
    
    def set_default_headers(self):
        super().set_default_headers()
        # Add CORS headers for images - support both common frontend ports
        origin = self.request.headers.get("Origin", "")
        allowed_origins = ["http://localhost:3000", "http://localhost:5173"]
        if origin in allowed_origins:
            self.set_header("Access-Control-Allow-Origin", origin)
        else:
            self.set_header("Access-Control-Allow-Origin", "http://localhost:3000")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")


class BulkImageUploadHandler(BaseHandler):
    """Handle bulk image uploads with automatic menu item matching"""
    
    def initialize(self):
        self.menu_controller = MenuController()
        self.upload_dir = config('UPLOAD_DIR', default='uploads')
        self.max_file_size = 10 * 1024 * 1024  # 10MB per file
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, 'menu_items'), exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, 'thumbnails'), exist_ok=True)
    
    async def post(self):
        """Upload multiple images and match them to menu items by filename"""
        try:
            # Get all uploaded files
            if not self.request.files:
                self.write_error_response(
                    ["No files provided"], 
                    400, 
                    "VALIDATION_ERROR"
                )
                return
            
            results = []
            errors = []
            
            # Get all menu items for matching
            menu_data = self.menu_controller.get_menu_items_by_filters(all=True)
            menu_items = menu_data['menu_items'] if menu_data else []
            menu_items_dict = {item['name'].lower().replace(' ', '_'): item for item in menu_items}
            
            # Process each uploaded file
            for field_name, file_list in self.request.files.items():
                for file_info in file_list:
                    try:
                        result = await self._process_single_file(file_info, menu_items_dict)
                        if result['success']:
                            results.append(result)
                        else:
                            errors.append(result)
                    except Exception as e:
                        errors.append({
                            'success': False,
                            'filename': file_info['filename'],
                            'error': str(e)
                        })
            
            response_data = {
                'uploaded': len(results),
                'failed': len(errors),
                'results': results,
                'errors': errors
            }
            
            if results:
                self.write_success(response_data, message=f"Processed {len(results)} images successfully")
            else:
                self.write_error_response(
                    ["No images were uploaded successfully"], 
                    400, 
                    "UPLOAD_FAILED"
                )
                
        except Exception as e:
            self.write_error_response(
                [f"Bulk upload failed: {str(e)}"], 
                500, 
                "BULK_UPLOAD_ERROR"
            )
    
    async def _process_single_file(self, file_info, menu_items_dict):
        """Process a single uploaded file"""
        filename = file_info['filename']
        file_body = file_info['body']
        
        # Validate file size
        if len(file_body) > self.max_file_size:
            return {
                'success': False,
                'filename': filename,
                'error': 'File size too large (max 10MB)'
            }
        
        # Validate file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in self.allowed_extensions:
            return {
                'success': False,
                'filename': filename,
                'error': f'Invalid file type. Allowed: {", ".join(self.allowed_extensions)}'
            }
        
        # Try to match filename to menu item
        base_name = os.path.splitext(filename)[0].lower().replace(' ', '_').replace('-', '_')
        
        # Try exact match first
        menu_item = menu_items_dict.get(base_name)
        
        # If no exact match, try partial matching
        if not menu_item:
            for item_name, item in menu_items_dict.items():
                if base_name in item_name or item_name in base_name:
                    menu_item = item
                    break
        
        if not menu_item:
            return {
                'success': False,
                'filename': filename,
                'error': 'No matching menu item found'
            }
        
        # Generate unique filename
        unique_filename = f"{menu_item['id']}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = os.path.join(self.upload_dir, 'menu_items', unique_filename)
        
        # Save original image
        with open(file_path, 'wb') as f:
            f.write(file_body)
        
        # Create thumbnail
        thumbnail_path = self._create_thumbnail(file_path, unique_filename)
        
        # Update menu item with image URL
        image_url = f"/uploads/menu_items/{unique_filename}"
        thumbnail_url = f"/uploads/thumbnails/{unique_filename}" if thumbnail_path else None
        
        updated_item = self.menu_controller.update_menu_item(
            menu_item['id'], 
            image_url=image_url
        )
        
        if updated_item:
            return {
                'success': True,
                'filename': filename,
                'menu_item_id': menu_item['id'],
                'menu_item_name': menu_item['name'],
                'image_url': image_url,
                'thumbnail_url': thumbnail_url,
                'file_size': len(file_body)
            }
        else:
            # Clean up uploaded file if database update failed
            if os.path.exists(file_path):
                os.remove(file_path)
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            
            return {
                'success': False,
                'filename': filename,
                'error': 'Failed to update menu item in database'
            }
    
    def _create_thumbnail(self, original_path, filename):
        """Create thumbnail version of uploaded image"""
        try:
            thumbnail_filename = filename
            thumbnail_path = os.path.join(self.upload_dir, 'thumbnails', thumbnail_filename)
            
            with Image.open(original_path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail (300x300 max, maintaining aspect ratio)
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
                
            return thumbnail_path
        except Exception as e:
            print(f"Failed to create thumbnail: {str(e)}")
            return None


class ImageManagementHandler(BaseHandler):
    """Handle image management operations"""
    
    def initialize(self):
        self.menu_controller = MenuController()
        self.upload_dir = config('UPLOAD_DIR', default='uploads')
    
    async def get(self):
        """Get all menu items with their image status"""
        try:
            menu_data = self.menu_controller.get_menu_items_by_filters(all=True)
            menu_items = menu_data['menu_items'] if menu_data else []
            
            items_data = []
            for item in menu_items:
                item_data = {
                    'id': item['id'],
                    'name': item['name'],
                    'size': item['size'],
                    'category': item['category'],
                    'imageUrl': item.get('imageUrl'),
                    'hasImage': bool(item.get('imageUrl')),
                    'thumbnailUrl': item['imageUrl'].replace('/menu_items/', '/thumbnails/') if item.get('imageUrl') else None
                }
                items_data.append(item_data)
            
            # Group by name for easier management
            grouped_items = {}
            for item in items_data:
                name = item['name']
                if name not in grouped_items:
                    grouped_items[name] = []
                grouped_items[name].append(item)
            
            response_data = {
                'items': items_data,
                'grouped_items': grouped_items,
                'total_items': len(items_data),
                'items_with_images': len([i for i in items_data if i['hasImage']]),
                'items_without_images': len([i for i in items_data if not i['hasImage']])
            }
            
            self.write_success(response_data, message="Image management data retrieved")
            
        except Exception as e:
            self.write_error_response(
                [f"Failed to get image management data: {str(e)}"], 
                500, 
                "INTERNAL_ERROR"
            )
    
    async def delete(self, item_id):
        """Remove image from menu item"""
        try:
            menu_item = self.menu_controller.get_menu_items_by_filters(id=item_id)
                
            if not menu_item:
                self.write_error_response(
                    ["Menu item not found"], 
                    404, 
                    "NOT_FOUND"
                )
                return
            
            # Remove image files if they exist
            if menu_item.get('imageUrl'):
                # Remove original image
                image_filename = os.path.basename(menu_item['imageUrl'])
                image_path = os.path.join(self.upload_dir, 'menu_items', image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                # Remove thumbnail
                thumbnail_path = os.path.join(self.upload_dir, 'thumbnails', image_filename)
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
            
            # Update menu item to remove image URL
            updated_item = self.menu_controller.update_menu_item(item_id, image_url=None)
            
            if updated_item:
                self.write_success(
                    {"menu_item_id": item_id}, 
                    message="Image removed successfully"
                )
            else:
                self.write_error_response(
                    ["Failed to update menu item"], 
                    500, 
                    "DATABASE_ERROR"
                )
                
        except Exception as e:
            self.write_error_response(
                [f"Failed to remove image: {str(e)}"], 
                500, 
                "INTERNAL_ERROR"
            )