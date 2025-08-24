#!/usr/bin/env python3
"""
Debug script to check what orders exist in the database
"""

import os
import sys
from datetime import datetime, timezone

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orm.db_init import session_scope
from orm.models.model_orders import Order, OrderStatus
from sqlalchemy import and_

def debug_orders():
    """Check what orders exist in the database"""
    print("Checking Orders in Database")
    print("=" * 50)
    
    try:
        with session_scope() as session:
            # Get all orders
            all_orders = session.query(Order).all()
            print(f"Total orders in database: {len(all_orders)}")
            
            if all_orders:
                print("\nRecent orders:")
                for i, order in enumerate(all_orders[-5:], 1):  # Show last 5 orders
                    print(f"{i}. Order {order.order_number}")
                    print(f"   ID: {order.id}")
                    print(f"   Total: ${order.total_amount}")
                    print(f"   Status: {order.status}")
                    print(f"   Created: {order.created_at}")
                    print(f"   Staff ID: {order.staff_id}")
                    print()
            
            # Check today's orders specifically
            today = datetime.now().date()
            start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
            
            print(f"Checking orders for today ({today}):")
            print(f"Start: {start_of_day}")
            print(f"End: {end_of_day}")
            
            today_orders = session.query(Order).filter(
                and_(
                    Order.created_at >= start_of_day,
                    Order.created_at <= end_of_day
                )
            ).all()
            
            print(f"\nToday's orders (all statuses): {len(today_orders)}")
            for order in today_orders:
                print(f"  - {order.order_number}: ${order.total_amount} ({order.status}) at {order.created_at}")
            
            # Check completed orders specifically
            completed_today = session.query(Order).filter(
                and_(
                    Order.created_at >= start_of_day,
                    Order.created_at <= end_of_day,
                    Order.status == OrderStatus.completed
                )
            ).all()
            
            print(f"\nToday's COMPLETED orders: {len(completed_today)}")
            for order in completed_today:
                print(f"  - {order.order_number}: ${order.total_amount} at {order.created_at}")
                
            # Check order items for one order
            if completed_today:
                sample_order = completed_today[0]
                print(f"\nOrder items for {sample_order.order_number}:")
                for item in sample_order.order_items:
                    print(f"  - {item.menu_item_name}: {item.quantity} x ${item.unit_price} = ${item.line_total}")
            
    except Exception as e:
        print(f"Error checking orders: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_orders()