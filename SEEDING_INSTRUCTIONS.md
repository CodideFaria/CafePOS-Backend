# CafePOS Database Seeding Instructions

## Overview
This document provides instructions for seeding the CafePOS database with production data, including menu items with EUR pricing and image URLs.

## Seeder Files

### 1. `seed_test_data.py` (Original)
- Contains basic test data
- Uses USD pricing
- Generic menu items without images
- Good for development and testing

### 2. `seed_production_data.py` (New)
- Contains actual production menu items
- Uses EUR pricing (1 USD ≈ 0.85 EUR conversion)
- Includes image URLs for all menu items
- Based on current production database

## Running the Seeders

### Prerequisites
1. Ensure your virtual environment is activated:
   ```bash
   cd CafePOS-Backend
   .venv/Scripts/activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

2. Ensure your database is running and configured in `.env`

### Option 1: Production Data Seeder (Recommended)
Run the new production seeder with EUR pricing:
```bash
python seed_production_data.py
```

This will create:
- 44+ Menu items with EUR pricing and image URLs
- 5 Users with different roles
- 12+ Inventory items with EUR pricing
- All prices converted from USD to EUR

### Option 2: Test Data Seeder
Run the original test seeder:
```bash
python seed_test_data.py
```

## Image Setup
The production seeder references images in `/uploads/menu_items/` directory. Make sure to:

1. Create the uploads directory structure:
   ```bash
   mkdir -p uploads/menu_items
   mkdir -p uploads/thumbnails
   ```

2. Copy your actual menu item images to `uploads/menu_items/` with the following naming convention:
   - `almond_croissant.png`
   - `americano_small.png`
   - `americano_medium.png`
   - `americano_large.png`
   - `avocado_toast.png`
   - `bagel.png`
   - `bagel_cream_cheese.png`
   - `banana_bread.png`
   - `blueberry_muffin.png`
   - `caesar_salad.png`
   - `cappuccino_small.png`
   - `cappuccino_medium.png`
   - `cappuccino_large.png`
   - `chai_latte_medium.png`
   - `chai_latte_large.png`
   - `chamomile_tea.png`
   - `chocolate_chip_muffin.png`
   - `cold_brew_medium.png`
   - `cold_brew_large.png`
   - `cortado.png`
   - `croissant.png`
   - `earl_grey.png`
   - `espresso_single.png`
   - `espresso_double.png`
   - `flat_white.png`
   - `frappuccino_medium.png`
   - `frappuccino_large.png`
   - `granola_bowl.png`
   - `green_tea.png`
   - `grilled_sandwich.png`
   - `hot_chocolate_small.png`
   - `hot_chocolate_medium.png`
   - `hot_chocolate_large.png`
   - `iced_coffee_medium.png`
   - `iced_coffee_large.png`
   - `iced_latte_medium.png`
   - `iced_latte_large.png`
   - `latte_small.png`
   - `latte_medium.png`
   - `latte_large.png`
   - `macchiato_small.png`
   - `macchiato_large.png`
   - `mocha_small.png`
   - `mocha_medium.png`
   - `mocha_large.png`
   - `pain_au_chocolat.png`

## Currency Conversion
The production seeder automatically converts USD prices to EUR using a rate of 0.85:
- Original: $4.25 → Converted: €3.61
- Original: $3.00 → Converted: €2.55
- etc.

## Frontend Updates
The frontend has been updated to display EUR (€) symbols instead of USD ($) throughout:
- Product cards
- Cart totals
- Checkout process
- Discount modal
- CSV import preview

## Login Credentials
After running either seeder, you can use these test accounts:
- **Admin**: username='admin', password='password123', pin='1234'
- **Manager**: username='manager', password='password123', pin='2345'  
- **Cashier**: username='cashier1', password='password123', pin='3456'

## Verification
After seeding, verify the data by:
1. Logging into the POS system
2. Checking that menu items display with EUR pricing
3. Verifying images load correctly (or show placeholder if images aren't added yet)
4. Testing the image upload system in Menu Management

## Notes
- The seeder will skip items that already exist (based on name/size combination)
- If you need to reset the database, drop and recreate it before running the seeder
- Image files are not included in the seeder - you need to add them manually
- The placeholder image system will show a professional food-themed placeholder if images are missing