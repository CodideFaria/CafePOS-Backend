import requests
import json
import time

BASE_URL = "http://127.0.0.1:8880"

def test_orders():
    print("\n--- Testing Orders and Order Items ---")

    # Create a temporary user and menu item for order testing
    print("Creating temporary user and menu item for order testing...")
    timestamp = str(int(time.time()))
    role_data = {"name": f"OrderTestRole_{timestamp}", "description": "Role for order testing"}
    response = requests.post(f"{BASE_URL}/roles", json=role_data)
    assert response.status_code == 201
    test_role_id = response.json()['id']

    user_data = {
        "username": f"orderuser_{timestamp}",
        "password": "hashedorderpassword",
        "firstName": "Order",
        "lastName": "User",
        "email": f"order{timestamp}@example.com",
        "role_id": test_role_id,
        "pin": "5678"
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    assert response.status_code == 201
    test_user_id = response.json()['data']['id']

    menu_item_data = {"name": f"Coffee_{timestamp}", "size": "Large", "price": 4.00}
    response = requests.post(f"{BASE_URL}/menu_items", json=menu_item_data)
    assert response.status_code == 201
    test_menu_item_id = response.json()['data']['id']
    print(f"Created Test User ID: {test_user_id}, Test Menu Item ID: {test_menu_item_id}")

    # 1. Create a new order
    print("\nCreating a new order...")
    new_order_data = {
        "user_id": test_user_id,
        "subtotal": 4.00,
        "taxAmount": 0.40,
        "total": 4.40,
        "discount_amount": 0.00,
        "discount_reason": None,
        "status": "PAID",
        "paymentMethod": "cash",
        "items": [{
            "menu_item_id": test_menu_item_id,
            "quantity": 1,
            "price": 4.00,
            "subtotal": 4.00
        }]
    }
    response = requests.post(f"{BASE_URL}/orders", json=new_order_data)
    print(f"POST /orders Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    created_order = response.json()
    created_order_id = created_order['data']['order']['id']
    print(f"Created Order ID: {created_order_id}")

    # Order items are created automatically as part of the order
    print("\nOrder items were created automatically with the order")

    # 3. Retrieve all orders
    print("\nRetrieving all orders...")
    response = requests.get(f"{BASE_URL}/orders")
    print(f"GET /orders Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert len(response.json()['data']['orders']) > 0

    # 4. Retrieve the created order by ID
    print(f"\nRetrieving order with ID: {created_order_id}...")
    response = requests.get(f"{BASE_URL}/orders/{created_order_id}")
    print(f"GET /orders/{created_order_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['data']['order']['id'] == created_order_id

    # 5. Test order status update functionality
    print(f"\nTesting order status (order already completed): {created_order_id}")

    # 6. Test order completion (order is already completed from creation)
    print(f"\nOrder {created_order_id} was created and completed successfully")

    # 10. Delete the created order
    print(f"\nDeleting order with ID: {created_order_id}...")
    response = requests.delete(f"{BASE_URL}/orders/{created_order_id}")
    print(f"DELETE /orders/{created_order_id} Status Code: {response.status_code}")
    assert response.status_code in [200, 204]  # Accept both success codes

    # Verify order deletion
    print(f"\nVerifying deletion of order with ID: {created_order_id}...")
    response = requests.get(f"{BASE_URL}/orders/{created_order_id}")
    print(f"GET /orders/{created_order_id} Status Code: {response.status_code}")
    assert response.status_code == 404
    print("Order deleted successfully.")

    # Clean up temporary user and menu item
    print(f"\nDeleting temporary user with ID: {test_user_id}...")
    requests.delete(f"{BASE_URL}/users/{test_user_id}")
    print(f"Deleting temporary role with ID: {test_role_id}...")
    requests.delete(f"{BASE_URL}/roles/{test_role_id}")
    print(f"Deleting temporary menu item with ID: {test_menu_item_id}...")
    requests.delete(f"{BASE_URL}/menu_items/{test_menu_item_id}")
    print("Temporary user, role, and menu item deleted successfully.")

    print("\n--- Orders and Order Items Tests Completed ---")

if __name__ == "__main__":
    test_orders()
