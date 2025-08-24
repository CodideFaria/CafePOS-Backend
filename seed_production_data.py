#!/usr/bin/env python3
"""
Production Data Seeder for CafePOS Backend
Seeds actual menu items with image URLs - converted to euros
"""

import sys
import os
from decimal import Decimal
from datetime import datetime, timezone

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orm.controllers.controller_menu import MenuController
from orm.controllers.controller_users import UserController
from orm.controllers.controller_inventory import InventoryController
from orm.controllers.controller_roles import RoleController
from orm.models.model_users import UserRole

def convert_usd_to_eur(usd_price):
    """Convert USD prices to EUR (approximately 1 USD = 0.85 EUR)"""
    return round(usd_price * 0.85, 2)

def seed_menu_items():
    """Seed menu items with actual data from production database (converted to EUR)"""
    print("Seeding production menu items with EUR pricing...")
    menu_controller = MenuController()
    
    # Current menu items from production database (converted to EUR)
    menu_items = [
        {"name": "Almond Croissant", "size": "Regular", "price": convert_usd_to_eur(4.25), "category": "Pastries", "description": "Croissant with almond cream", "image_url": "/uploads/menu_items/almond_croissant.png"},
        {"name": "Americano", "size": "Small", "price": convert_usd_to_eur(3.0), "category": "Coffee", "description": "Espresso with hot water", "image_url": "/uploads/menu_items/americano_small.png"},
        {"name": "Americano", "size": "Large", "price": convert_usd_to_eur(4.0), "category": "Coffee", "description": "Espresso with hot water", "image_url": "/uploads/menu_items/americano_large.png"},
        {"name": "Americano", "size": "Medium", "price": convert_usd_to_eur(3.5), "category": "Coffee", "description": "Espresso with hot water", "image_url": "/uploads/menu_items/americano_medium.png"},
        {"name": "Avocado Toast", "size": "Regular", "price": convert_usd_to_eur(6.5), "category": "Food", "description": "Toasted bread with avocado", "image_url": "/uploads/menu_items/avocado_toast.png"},
        {"name": "Bagel", "size": "Regular", "price": convert_usd_to_eur(2.75), "category": "Food", "description": "Fresh baked bagel", "image_url": "/uploads/menu_items/bagel.png"},
        {"name": "Bagel with Cream Cheese", "size": "Regular", "price": convert_usd_to_eur(4.25), "category": "Food", "description": "Bagel with cream cheese", "image_url": "/uploads/menu_items/bagel_cream_cheese.png"},
        {"name": "Banana Bread", "size": "Slice", "price": convert_usd_to_eur(3.0), "category": "Pastries", "description": "Moist banana bread", "image_url": "/uploads/menu_items/banana_bread.png"},
        {"name": "Blueberry Muffin", "size": "Regular", "price": convert_usd_to_eur(3.5), "category": "Pastries", "description": "Fresh blueberry muffin", "image_url": "/uploads/menu_items/blueberry_muffin.png"},
        {"name": "Caesar Salad", "size": "Regular", "price": convert_usd_to_eur(8.95), "category": "Food", "description": "Fresh Caesar salad", "image_url": "/uploads/menu_items/caesar_salad.png"},
        {"name": "Cappuccino", "size": "Medium", "price": convert_usd_to_eur(4.75), "category": "Coffee", "description": "Espresso with steamed milk and foam", "image_url": "/uploads/menu_items/cappuccino_medium.png"},
        {"name": "Cappuccino", "size": "Large", "price": convert_usd_to_eur(5.0), "category": "Coffee", "description": "Espresso with steamed milk and foam", "image_url": "/uploads/menu_items/cappuccino_large.png"},
        {"name": "Cappuccino", "size": "Small", "price": convert_usd_to_eur(4.25), "category": "Coffee", "description": "Espresso with steamed milk and foam", "image_url": "/uploads/menu_items/cappuccino_small.png"},
        {"name": "Chai Latte", "size": "Medium", "price": convert_usd_to_eur(4.25), "category": "Tea", "description": "Spiced tea with steamed milk", "image_url": "/uploads/menu_items/chai_latte_medium.png"},
        {"name": "Chai Latte", "size": "Large", "price": convert_usd_to_eur(4.75), "category": "Tea", "description": "Spiced tea with steamed milk", "image_url": "/uploads/menu_items/chai_latte_large.png"},
        {"name": "Chamomile Tea", "size": "Medium", "price": convert_usd_to_eur(2.75), "category": "Tea", "description": "Soothing herbal tea", "image_url": "/uploads/menu_items/chamomile_tea.png"},
        {"name": "Chocolate Chip Muffin", "size": "Regular", "price": convert_usd_to_eur(3.5), "category": "Pastries", "description": "Classic chocolate chip muffin", "image_url": "/uploads/menu_items/chocolate_chip_muffin.png"},
        {"name": "Cold Brew", "size": "Medium", "price": convert_usd_to_eur(4.0), "category": "Cold Coffee", "description": "Smooth cold-brewed coffee", "image_url": "/uploads/menu_items/cold_brew_medium.png"},
        {"name": "Cold Brew", "size": "Large", "price": convert_usd_to_eur(4.5), "category": "Cold Coffee", "description": "Smooth cold-brewed coffee", "image_url": "/uploads/menu_items/cold_brew_large.png"},
        {"name": "Cortado", "size": "Small", "price": convert_usd_to_eur(4.25), "category": "Coffee", "description": "Equal parts espresso and warm milk", "image_url": "/uploads/menu_items/cortado.png"},
        {"name": "Croissant", "size": "Regular", "price": convert_usd_to_eur(3.25), "category": "Pastries", "description": "Buttery, flaky pastry", "image_url": "/uploads/menu_items/croissant.png"},
        {"name": "Earl Grey", "size": "Medium", "price": convert_usd_to_eur(2.75), "category": "Tea", "description": "Classic bergamot-flavored tea", "image_url": "/uploads/menu_items/earl_grey.png"},
        {"name": "Espresso", "size": "Double", "price": convert_usd_to_eur(3.5), "category": "Coffee", "description": "Double shot of concentrated coffee", "image_url": "/uploads/menu_items/espresso_double.png"},
        {"name": "Espresso", "size": "Single", "price": convert_usd_to_eur(2.5), "category": "Coffee", "description": "Strong, concentrated coffee shot", "image_url": "/uploads/menu_items/espresso_single.png"},
        {"name": "Flat White", "size": "Small", "price": convert_usd_to_eur(4.5), "category": "Coffee", "description": "Double shot with steamed milk", "image_url": "/uploads/menu_items/flat_white.png"},
        {"name": "Frappuccino", "size": "Large", "price": convert_usd_to_eur(6.0), "category": "Cold Coffee", "description": "Blended coffee with ice and milk", "image_url": "/uploads/menu_items/frappuccino_large.png"},
        {"name": "Frappuccino", "size": "Medium", "price": convert_usd_to_eur(5.5), "category": "Cold Coffee", "description": "Blended coffee with ice and milk", "image_url": "/uploads/menu_items/frappuccino_medium.png"},
        {"name": "Granola Bowl", "size": "Regular", "price": convert_usd_to_eur(6.75), "category": "Food", "description": "Granola with yogurt and fruit", "image_url": "/uploads/menu_items/granola_bowl.png"},
        {"name": "Green Tea", "size": "Medium", "price": convert_usd_to_eur(2.75), "category": "Tea", "description": "Premium green tea", "image_url": "/uploads/menu_items/green_tea.png"},
        {"name": "Grilled Sandwich", "size": "Regular", "price": convert_usd_to_eur(7.95), "category": "Food", "description": "Grilled cheese and ham sandwich", "image_url": "/uploads/menu_items/grilled_sandwich.png"},
        {"name": "Hot Chocolate", "size": "Small", "price": convert_usd_to_eur(3.5), "category": "Hot Beverages", "description": "Rich chocolate drink", "image_url": "/uploads/menu_items/hot_chocolate_small.png"},
        {"name": "Hot Chocolate", "size": "Medium", "price": convert_usd_to_eur(4.0), "category": "Hot Beverages", "description": "Rich chocolate drink", "image_url": "/uploads/menu_items/hot_chocolate_medium.png"},
        {"name": "Hot Chocolate", "size": "Large", "price": convert_usd_to_eur(4.5), "category": "Hot Beverages", "description": "Rich chocolate drink", "image_url": "/uploads/menu_items/hot_chocolate_large.png"},
        {"name": "Iced Coffee", "size": "Large", "price": convert_usd_to_eur(3.75), "category": "Cold Coffee", "description": "Chilled brewed coffee over ice", "image_url": "/uploads/menu_items/iced_coffee_large.png"},
        {"name": "Iced Coffee", "size": "Medium", "price": convert_usd_to_eur(3.25), "category": "Cold Coffee", "description": "Chilled brewed coffee over ice", "image_url": "/uploads/menu_items/iced_coffee_medium.png"},
        {"name": "Iced Latte", "size": "Medium", "price": convert_usd_to_eur(4.75), "category": "Cold Coffee", "description": "Espresso with cold milk over ice", "image_url": "/uploads/menu_items/iced_latte_medium.png"},
        {"name": "Iced Latte", "size": "Large", "price": convert_usd_to_eur(5.25), "category": "Cold Coffee", "description": "Espresso with cold milk over ice", "image_url": "/uploads/menu_items/iced_latte_large.png"},
        {"name": "Latte", "size": "Small", "price": convert_usd_to_eur(4.5), "category": "Coffee", "description": "Espresso with steamed milk", "image_url": "/uploads/menu_items/latte_small.png"},
        {"name": "Latte", "size": "Large", "price": convert_usd_to_eur(5.5), "category": "Coffee", "description": "Espresso with steamed milk", "image_url": "/uploads/menu_items/latte_large.png"},
        {"name": "Latte", "size": "Medium", "price": convert_usd_to_eur(4.5), "category": "Coffee", "description": "Espresso with steamed milk", "image_url": "/uploads/menu_items/latte_medium.png"},
        {"name": "Macchiato", "size": "Large", "price": convert_usd_to_eur(5.25), "category": "Coffee", "description": "Espresso marked with steamed milk", "image_url": "/uploads/menu_items/macchiato_large.png"},
        {"name": "Macchiato", "size": "Small", "price": convert_usd_to_eur(4.75), "category": "Coffee", "description": "Espresso marked with steamed milk", "image_url": "/uploads/menu_items/macchiato_small.png"},
        {"name": "Mocha", "size": "Small", "price": convert_usd_to_eur(5.0), "category": "Coffee", "description": "Espresso with chocolate and steamed milk", "image_url": "/uploads/menu_items/mocha_small.png"},
        {"name": "Mocha", "size": "Medium", "price": convert_usd_to_eur(5.5), "category": "Coffee", "description": "Espresso with chocolate and steamed milk", "image_url": "/uploads/menu_items/mocha_medium.png"},
        {"name": "Mocha", "size": "Large", "price": convert_usd_to_eur(6.0), "category": "Coffee", "description": "Espresso with chocolate and steamed milk", "image_url": "/uploads/menu_items/mocha_large.png"},
        {"name": "Pain au Chocolat", "size": "Regular", "price": convert_usd_to_eur(3.75), "category": "Pastries", "description": "Croissant with chocolate", "image_url": "/uploads/menu_items/pain_au_chocolat.png"},
    ]
    
    created_count = 0
    for item in menu_items:
        try:
            menu_controller.create_menu_item(**item)
            created_count += 1
        except Exception as e:
            print(f"Error creating menu item {item['name']}: {e}")
    
    print(f"Created {created_count} menu items with EUR pricing")

def seed_users():
    """Seed users with different roles"""
    print("Seeding users...")
    user_controller = UserController()
    
    users = [
        {
            "username": "admin",
            "password": "password123",
            "first_name": "Admin",
            "last_name": "User",
            "email": "admin@cafepos.com",
            "role": UserRole.admin,
            "pin_code": "1234"
        },
        {
            "username": "manager",
            "password": "password123",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": "manager@cafepos.com",
            "role": UserRole.manager,
            "pin_code": "2345"
        },
        {
            "username": "cashier1",
            "password": "password123",
            "first_name": "Mike",
            "last_name": "Wilson",
            "email": "mike@cafepos.com",
            "role": UserRole.cashier,
            "pin_code": "3456"
        },
        {
            "username": "cashier2",
            "password": "password123",
            "first_name": "Emma",
            "last_name": "Davis",
            "email": "emma@cafepos.com",
            "role": UserRole.cashier,
            "pin_code": "4567"
        },
        {
            "username": "trainee",
            "password": "password123",
            "first_name": "Alex",
            "last_name": "Brown",
            "email": "trainee@cafepos.com",
            "role": UserRole.trainee,
            "pin_code": "5678"
        }
    ]
    
    created_count = 0
    for user in users:
        try:
            user_controller.create_user(**user)
            created_count += 1
        except Exception as e:
            print(f"Error creating user {user['username']}: {e}")
    
    print(f"Created {created_count} users")

def seed_inventory():
    """Seed inventory items with EUR pricing"""
    print("Seeding inventory with EUR pricing...")
    inventory_controller = InventoryController()
    
    inventory_items = [
        # Coffee & Beans (converted to EUR)
        {"name": "Arabica Coffee Beans", "category": "Coffee", "current_stock": 50.0, "min_stock_level": 10.0, "max_stock_level": 100.0, 
         "unit": "kg", "cost_per_unit": convert_usd_to_eur(12.50), "supplier": "Premium Coffee Co", "description": "High-quality arabica beans"},
        {"name": "Robusta Coffee Beans", "category": "Coffee", "current_stock": 30.0, "min_stock_level": 5.0, "max_stock_level": 50.0,
         "unit": "kg", "cost_per_unit": convert_usd_to_eur(8.75), "supplier": "Premium Coffee Co", "description": "Strong robusta beans"},
        {"name": "Decaf Coffee Beans", "category": "Coffee", "current_stock": 15.0, "min_stock_level": 5.0, "max_stock_level": 25.0,
         "unit": "kg", "cost_per_unit": convert_usd_to_eur(11.25), "supplier": "Premium Coffee Co", "description": "Decaffeinated beans"},
        
        # Dairy & Milk (converted to EUR)
        {"name": "Whole Milk", "category": "Dairy", "current_stock": 40.0, "min_stock_level": 10.0, "max_stock_level": 60.0,
         "unit": "liters", "cost_per_unit": convert_usd_to_eur(1.25), "supplier": "Local Dairy Farm", "description": "Fresh whole milk"},
        {"name": "Oat Milk", "category": "Dairy", "current_stock": 25.0, "min_stock_level": 5.0, "max_stock_level": 40.0,
         "unit": "liters", "cost_per_unit": convert_usd_to_eur(2.75), "supplier": "Plant Milk Co", "description": "Organic oat milk"},
        {"name": "Almond Milk", "category": "Dairy", "current_stock": 20.0, "min_stock_level": 5.0, "max_stock_level": 35.0,
         "unit": "liters", "cost_per_unit": convert_usd_to_eur(3.25), "supplier": "Plant Milk Co", "description": "Unsweetened almond milk"},
        
        # Syrups & Flavoring (converted to EUR)
        {"name": "Vanilla Syrup", "category": "Syrups", "current_stock": 12.0, "min_stock_level": 3.0, "max_stock_level": 20.0,
         "unit": "bottles", "cost_per_unit": convert_usd_to_eur(8.95), "supplier": "Flavor House", "description": "Premium vanilla syrup"},
        {"name": "Caramel Syrup", "category": "Syrups", "current_stock": 10.0, "min_stock_level": 3.0, "max_stock_level": 20.0,
         "unit": "bottles", "cost_per_unit": convert_usd_to_eur(8.95), "supplier": "Flavor House", "description": "Rich caramel syrup"},
        
        # Pastries & Baked Goods (converted to EUR)
        {"name": "Croissants", "category": "Pastries", "current_stock": 24.0, "min_stock_level": 6.0, "max_stock_level": 50.0,
         "unit": "pieces", "cost_per_unit": convert_usd_to_eur(1.25), "supplier": "French Bakery", "description": "Fresh croissants"},
        {"name": "Muffins", "category": "Pastries", "current_stock": 36.0, "min_stock_level": 12.0, "max_stock_level": 60.0,
         "unit": "pieces", "cost_per_unit": convert_usd_to_eur(1.50), "supplier": "Local Bakery", "description": "Assorted muffins"},
        
        # Supplies (converted to EUR)
        {"name": "Paper Cups", "category": "Supplies", "current_stock": 2000.0, "min_stock_level": 500.0, "max_stock_level": 5000.0,
         "unit": "pieces", "cost_per_unit": convert_usd_to_eur(0.15), "supplier": "Cup Supply Inc", "description": "8oz disposable cups"},
        {"name": "Cup Lids", "category": "Supplies", "current_stock": 1800.0, "min_stock_level": 400.0, "max_stock_level": 4000.0,
         "unit": "pieces", "cost_per_unit": convert_usd_to_eur(0.08), "supplier": "Cup Supply Inc", "description": "Disposable cup lids"},
    ]
    
    created_count = 0
    for item in inventory_items:
        try:
            inventory_controller.create_inventory_item(**item)
            created_count += 1
        except Exception as e:
            print(f"Error creating inventory item {item['name']}: {e}")
    
    print(f"Created {created_count} inventory items with EUR pricing")

def seed_roles():
    """Seed roles if using role-based system"""
    print("Seeding roles...")
    try:
        role_controller = RoleController()
        
        roles = [
            {"name": "admin", "description": "System administrator with full access"},
            {"name": "manager", "description": "Store manager with management permissions"},
            {"name": "cashier", "description": "Cashier with POS access"},
            {"name": "trainee", "description": "Trainee with limited access"}
        ]
        
        created_count = 0
        for role in roles:
            try:
                role_controller.create_role(**role)
                created_count += 1
            except Exception as e:
                print(f"Error creating role {role['name']}: {e}")
        
        print(f"Created {created_count} roles")
    except ImportError:
        print("Role controller not available, skipping role seeding")

def main():
    """Run all seeders with EUR conversion"""
    print("Starting CafePOS Production Data Seeding with EUR Currency...")
    print("=" * 60)
    
    try:
        # Seed in order of dependencies
        seed_roles()
        seed_users()
        seed_menu_items()
        seed_inventory()
        
        print("=" * 60)
        print("Production seeding completed successfully!")
        print("\nProduction Data Summary:")
        print("* 44+ Menu items with EUR pricing and image URLs")
        print("* 5 Users with different roles (admin, manager, cashiers, trainee)")
        print("* 12+ Inventory items with EUR pricing")
        print("* All prices converted from USD to EUR (1 USD ≈ 0.85 EUR)")
        print("\nTest Login Credentials:")
        print("* Admin: username='admin', password='password123', pin='1234'")
        print("* Manager: username='manager', password='password123', pin='2345'")
        print("* Cashier: username='cashier1', password='password123', pin='3456'")
        print("\nYour CafePOS backend is ready for production with EUR pricing!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()