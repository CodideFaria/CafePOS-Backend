#!/usr/bin/env python3
"""
Test Data Seeder for CafePOS Backend
Seeds comprehensive test data using existing controllers
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

def seed_menu_items():
    """Seed menu items with comprehensive coffee shop offerings"""
    print("Seeding menu items...")
    menu_controller = MenuController()
    
    menu_items = [
        # Coffee Drinks
        {"name": "Espresso", "size": "Single", "price": 2.50, "category": "Coffee", "description": "Strong, concentrated coffee shot"},
        {"name": "Espresso", "size": "Double", "price": 3.50, "category": "Coffee", "description": "Double shot of concentrated coffee"},
        {"name": "Americano", "size": "Small", "price": 3.00, "category": "Coffee", "description": "Espresso with hot water"},
        {"name": "Americano", "size": "Medium", "price": 3.50, "category": "Coffee", "description": "Espresso with hot water"},
        {"name": "Americano", "size": "Large", "price": 4.00, "category": "Coffee", "description": "Espresso with hot water"},
        {"name": "Latte", "size": "Small", "price": 4.50, "category": "Coffee", "description": "Espresso with steamed milk"},
        {"name": "Latte", "size": "Medium", "price": 5.00, "category": "Coffee", "description": "Espresso with steamed milk"},
        {"name": "Latte", "size": "Large", "price": 5.50, "category": "Coffee", "description": "Espresso with steamed milk"},
        {"name": "Cappuccino", "size": "Small", "price": 4.25, "category": "Coffee", "description": "Espresso with steamed milk and foam"},
        {"name": "Cappuccino", "size": "Medium", "price": 4.75, "category": "Coffee", "description": "Espresso with steamed milk and foam"},
        {"name": "Cappuccino", "size": "Large", "price": 5.25, "category": "Coffee", "description": "Espresso with steamed milk and foam"},
        {"name": "Macchiato", "size": "Small", "price": 4.75, "category": "Coffee", "description": "Espresso marked with steamed milk"},
        {"name": "Macchiato", "size": "Large", "price": 5.25, "category": "Coffee", "description": "Espresso marked with steamed milk"},
        {"name": "Mocha", "size": "Small", "price": 5.00, "category": "Coffee", "description": "Espresso with chocolate and steamed milk"},
        {"name": "Mocha", "size": "Medium", "price": 5.50, "category": "Coffee", "description": "Espresso with chocolate and steamed milk"},
        {"name": "Mocha", "size": "Large", "price": 6.00, "category": "Coffee", "description": "Espresso with chocolate and steamed milk"},
        {"name": "Flat White", "size": "Small", "price": 4.50, "category": "Coffee", "description": "Double shot with steamed milk"},
        {"name": "Cortado", "size": "Small", "price": 4.25, "category": "Coffee", "description": "Equal parts espresso and warm milk"},
        
        # Cold Coffee
        {"name": "Iced Coffee", "size": "Medium", "price": 3.25, "category": "Cold Coffee", "description": "Chilled brewed coffee over ice"},
        {"name": "Iced Coffee", "size": "Large", "price": 3.75, "category": "Cold Coffee", "description": "Chilled brewed coffee over ice"},
        {"name": "Cold Brew", "size": "Medium", "price": 4.00, "category": "Cold Coffee", "description": "Smooth cold-brewed coffee"},
        {"name": "Cold Brew", "size": "Large", "price": 4.50, "category": "Cold Coffee", "description": "Smooth cold-brewed coffee"},
        {"name": "Iced Latte", "size": "Medium", "price": 4.75, "category": "Cold Coffee", "description": "Espresso with cold milk over ice"},
        {"name": "Iced Latte", "size": "Large", "price": 5.25, "category": "Cold Coffee", "description": "Espresso with cold milk over ice"},
        {"name": "Frappuccino", "size": "Medium", "price": 5.50, "category": "Cold Coffee", "description": "Blended coffee with ice and milk"},
        {"name": "Frappuccino", "size": "Large", "price": 6.00, "category": "Cold Coffee", "description": "Blended coffee with ice and milk"},
        
        # Tea & Other Beverages
        {"name": "Green Tea", "size": "Medium", "price": 2.75, "category": "Tea", "description": "Premium green tea"},
        {"name": "Earl Grey", "size": "Medium", "price": 2.75, "category": "Tea", "description": "Classic bergamot-flavored tea"},
        {"name": "Chamomile", "size": "Medium", "price": 2.75, "category": "Tea", "description": "Soothing herbal tea"},
        {"name": "Chai Latte", "size": "Medium", "price": 4.25, "category": "Tea", "description": "Spiced tea with steamed milk"},
        {"name": "Chai Latte", "size": "Large", "price": 4.75, "category": "Tea", "description": "Spiced tea with steamed milk"},
        {"name": "Hot Chocolate", "size": "Small", "price": 3.50, "category": "Hot Beverages", "description": "Rich chocolate drink"},
        {"name": "Hot Chocolate", "size": "Medium", "price": 4.00, "category": "Hot Beverages", "description": "Rich chocolate drink"},
        {"name": "Hot Chocolate", "size": "Large", "price": 4.50, "category": "Hot Beverages", "description": "Rich chocolate drink"},
        
        # Pastries & Food
        {"name": "Croissant", "size": "Regular", "price": 3.25, "category": "Pastries", "description": "Buttery, flaky pastry"},
        {"name": "Pain au Chocolat", "size": "Regular", "price": 3.75, "category": "Pastries", "description": "Croissant with chocolate"},
        {"name": "Almond Croissant", "size": "Regular", "price": 4.25, "category": "Pastries", "description": "Croissant with almond cream"},
        {"name": "Blueberry Muffin", "size": "Regular", "price": 3.50, "category": "Pastries", "description": "Fresh blueberry muffin"},
        {"name": "Chocolate Chip Muffin", "size": "Regular", "price": 3.50, "category": "Pastries", "description": "Classic chocolate chip muffin"},
        {"name": "Banana Bread", "size": "Slice", "price": 3.00, "category": "Pastries", "description": "Moist banana bread"},
        {"name": "Bagel", "size": "Regular", "price": 2.75, "category": "Food", "description": "Fresh baked bagel"},
        {"name": "Bagel with Cream Cheese", "size": "Regular", "price": 4.25, "category": "Food", "description": "Bagel with cream cheese"},
        {"name": "Avocado Toast", "size": "Regular", "price": 6.50, "category": "Food", "description": "Toasted bread with avocado"},
        {"name": "Grilled Sandwich", "size": "Regular", "price": 7.95, "category": "Food", "description": "Grilled cheese and ham sandwich"},
        {"name": "Caesar Salad", "size": "Regular", "price": 8.95, "category": "Food", "description": "Fresh Caesar salad"},
        {"name": "Granola Bowl", "size": "Regular", "price": 6.75, "category": "Food", "description": "Granola with yogurt and fruit"},
    ]
    
    created_count = 0
    for item in menu_items:
        try:
            menu_controller.create_menu_item(**item)
            created_count += 1
        except Exception as e:
            print(f"Error creating menu item {item['name']}: {e}")
    
    print(f"Created {created_count} menu items")

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
    """Seed inventory items"""
    print("Seeding inventory...")
    inventory_controller = InventoryController()
    
    inventory_items = [
        # Coffee & Beans
        {"name": "Arabica Coffee Beans", "category": "Coffee", "current_stock": 50.0, "min_stock_level": 10.0, "max_stock_level": 100.0, 
         "unit": "kg", "cost_per_unit": 12.50, "supplier": "Premium Coffee Co", "description": "High-quality arabica beans"},
        {"name": "Robusta Coffee Beans", "category": "Coffee", "current_stock": 30.0, "min_stock_level": 5.0, "max_stock_level": 50.0,
         "unit": "kg", "cost_per_unit": 8.75, "supplier": "Premium Coffee Co", "description": "Strong robusta beans"},
        {"name": "Decaf Coffee Beans", "category": "Coffee", "current_stock": 15.0, "min_stock_level": 5.0, "max_stock_level": 25.0,
         "unit": "kg", "cost_per_unit": 11.25, "supplier": "Premium Coffee Co", "description": "Decaffeinated beans"},
        
        # Dairy & Milk
        {"name": "Whole Milk", "category": "Dairy", "current_stock": 40.0, "min_stock_level": 10.0, "max_stock_level": 60.0,
         "unit": "liters", "cost_per_unit": 1.25, "supplier": "Local Dairy Farm", "description": "Fresh whole milk"},
        {"name": "Oat Milk", "category": "Dairy", "current_stock": 25.0, "min_stock_level": 5.0, "max_stock_level": 40.0,
         "unit": "liters", "cost_per_unit": 2.75, "supplier": "Plant Milk Co", "description": "Organic oat milk"},
        {"name": "Almond Milk", "category": "Dairy", "current_stock": 20.0, "min_stock_level": 5.0, "max_stock_level": 35.0,
         "unit": "liters", "cost_per_unit": 3.25, "supplier": "Plant Milk Co", "description": "Unsweetened almond milk"},
        {"name": "Heavy Cream", "category": "Dairy", "current_stock": 8.0, "min_stock_level": 2.0, "max_stock_level": 15.0,
         "unit": "liters", "cost_per_unit": 4.50, "supplier": "Local Dairy Farm", "description": "Fresh heavy cream"},
        
        # Syrups & Flavoring
        {"name": "Vanilla Syrup", "category": "Syrups", "current_stock": 12.0, "min_stock_level": 3.0, "max_stock_level": 20.0,
         "unit": "bottles", "cost_per_unit": 8.95, "supplier": "Flavor House", "description": "Premium vanilla syrup"},
        {"name": "Caramel Syrup", "category": "Syrups", "current_stock": 10.0, "min_stock_level": 3.0, "max_stock_level": 20.0,
         "unit": "bottles", "cost_per_unit": 8.95, "supplier": "Flavor House", "description": "Rich caramel syrup"},
        {"name": "Hazelnut Syrup", "category": "Syrups", "current_stock": 8.0, "min_stock_level": 2.0, "max_stock_level": 15.0,
         "unit": "bottles", "cost_per_unit": 9.50, "supplier": "Flavor House", "description": "Nutty hazelnut syrup"},
        {"name": "Chocolate Syrup", "category": "Syrups", "current_stock": 15.0, "min_stock_level": 4.0, "max_stock_level": 25.0,
         "unit": "bottles", "cost_per_unit": 7.75, "supplier": "Choco Delights", "description": "Rich chocolate syrup"},
        
        # Pastries & Baked Goods
        {"name": "Croissants", "category": "Pastries", "current_stock": 24.0, "min_stock_level": 6.0, "max_stock_level": 50.0,
         "unit": "pieces", "cost_per_unit": 1.25, "supplier": "French Bakery", "description": "Fresh croissants"},
        {"name": "Muffins", "category": "Pastries", "current_stock": 36.0, "min_stock_level": 12.0, "max_stock_level": 60.0,
         "unit": "pieces", "cost_per_unit": 1.50, "supplier": "Local Bakery", "description": "Assorted muffins"},
        {"name": "Bagels", "category": "Food", "current_stock": 48.0, "min_stock_level": 12.0, "max_stock_level": 80.0,
         "unit": "pieces", "cost_per_unit": 0.85, "supplier": "Bagel Shop", "description": "Fresh bagels"},
        
        # Tea & Other
        {"name": "Green Tea Bags", "category": "Tea", "current_stock": 200.0, "min_stock_level": 50.0, "max_stock_level": 500.0,
         "unit": "bags", "cost_per_unit": 0.25, "supplier": "Tea Masters", "description": "Premium green tea"},
        {"name": "Earl Grey Tea Bags", "category": "Tea", "current_stock": 150.0, "min_stock_level": 30.0, "max_stock_level": 300.0,
         "unit": "bags", "cost_per_unit": 0.30, "supplier": "Tea Masters", "description": "Classic Earl Grey"},
        {"name": "Sugar", "category": "Supplies", "current_stock": 25.0, "min_stock_level": 5.0, "max_stock_level": 50.0,
         "unit": "kg", "cost_per_unit": 2.25, "supplier": "Sweet Supply Co", "description": "White granulated sugar"},
        {"name": "Paper Cups", "category": "Supplies", "current_stock": 2000.0, "min_stock_level": 500.0, "max_stock_level": 5000.0,
         "unit": "pieces", "cost_per_unit": 0.15, "supplier": "Cup Supply Inc", "description": "8oz disposable cups"},
        {"name": "Cup Lids", "category": "Supplies", "current_stock": 1800.0, "min_stock_level": 400.0, "max_stock_level": 4000.0,
         "unit": "pieces", "cost_per_unit": 0.08, "supplier": "Cup Supply Inc", "description": "Disposable cup lids"},
        
        # Low stock items for testing alerts
        {"name": "Soy Milk", "category": "Dairy", "current_stock": 2.0, "min_stock_level": 5.0, "max_stock_level": 30.0,
         "unit": "liters", "cost_per_unit": 2.95, "supplier": "Plant Milk Co", "description": "Organic soy milk"},
        {"name": "Cinnamon Syrup", "category": "Syrups", "current_stock": 1.0, "min_stock_level": 3.0, "max_stock_level": 15.0,
         "unit": "bottles", "cost_per_unit": 9.25, "supplier": "Flavor House", "description": "Warm cinnamon syrup"},
    ]
    
    created_count = 0
    for item in inventory_items:
        try:
            inventory_controller.create_inventory_item(**item)
            created_count += 1
        except Exception as e:
            print(f"Error creating inventory item {item['name']}: {e}")
    
    print(f"Created {created_count} inventory items")

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
    """Run all seeders"""
    print("Starting CafePOS Test Data Seeding...")
    print("=" * 50)
    
    try:
        # Seed in order of dependencies
        seed_roles()
        seed_users()
        seed_menu_items()
        seed_inventory()
        
        print("=" * 50)
        print("Seeding completed successfully!")
        print("\nTest Data Summary:")
        print("* 45+ Menu items across coffee, tea, food categories")
        print("* 5 Users with different roles (admin, manager, cashiers, trainee)")
        print("* 20+ Inventory items with realistic stock levels")
        print("* Some low-stock items for testing alerts")
        print("\nTest Login Credentials:")
        print("* Admin: username='admin', password='password123', pin='1234'")
        print("* Manager: username='manager', password='password123', pin='2345'")
        print("* Cashier: username='cashier1', password='password123', pin='3456'")
        print("\nYour CafePOS backend is ready for testing!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()