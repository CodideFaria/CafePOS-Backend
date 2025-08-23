import requests
import json

BASE_URL = "http://127.0.0.1:8888"

def test_orders():
    print("\n--- Testing Orders and Order Items ---")

    # Create a temporary user and menu item for order testing
    print("Creating temporary user and menu item for order testing...")
    role_data = {"name": "OrderTestRole", "description": "Role for order testing"}
    response = requests.post(f"{BASE_URL}/roles", json=role_data)
    assert response.status_code == 201
    test_role_id = response.json()['id']

    user_data = {
        "username": "orderuser",
        "hashed_password": "hashedorderpassword",
        "role_id": test_role_id,
        "pin": "5678"
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    assert response.status_code == 201
    test_user_id = response.json()['id']

    menu_item_data = {"name": "Coffee", "size": "Large", "price": 4.00}
    response = requests.post(f"{BASE_URL}/menu_items", json=menu_item_data)
    assert response.status_code == 201
    test_menu_item_id = response.json()['id']
    print(f"Created Test User ID: {test_user_id}, Test Menu Item ID: {test_menu_item_id}")

    # 1. Create a new order
    print("\nCreating a new order...")
    new_order_data = {
        "user_id": test_user_id,
        "subtotal": 4.00,
        "tax": 0.40,
        "total": 4.40,
        "discount_amount": 0.00,
        "discount_reason": None,
        "status": "PAID"
    }
    response = requests.post(f"{BASE_URL}/orders", json=new_order_data)
    print(f"POST /orders Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    created_order = response.json()
    created_order_id = created_order['id']
    print(f"Created Order ID: {created_order_id}")

    # 2. Create an order item for the new order
    print("\nCreating an order item...")
    new_order_item_data = {
        "order_id": created_order_id,
        "menu_item_id": test_menu_item_id,
        "quantity": 1,
        "price_at_time_of_sale": 4.00
    }
    response = requests.post(f"{BASE_URL}/order_items", json=new_order_item_data)
    print(f"POST /order_items Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    created_order_item = response.json()
    created_order_item_id = created_order_item['id']
    print(f"Created Order Item ID: {created_order_item_id}")

    # 3. Retrieve all orders
    print("\nRetrieving all orders...")
    response = requests.get(f"{BASE_URL}/orders")
    print(f"GET /orders Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert len(response.json()['orders']) > 0

    # 4. Retrieve the created order by ID
    print(f"\nRetrieving order with ID: {created_order_id}...")
    response = requests.get(f"{BASE_URL}/orders/{created_order_id}")
    print(f"GET /orders/{created_order_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['id'] == created_order_id

    # 5. Retrieve all order items
    print("\nRetrieving all order items...")
    response = requests.get(f"{BASE_URL}/order_items")
    print(f"GET /order_items Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert len(response.json()['order_items']) > 0

    # 6. Retrieve the created order item by ID
    print(f"\nRetrieving order item with ID: {created_order_item_id}...")
    response = requests.get(f"{BASE_URL}/order_items/{created_order_item_id}")
    print(f"GET /order_items/{created_order_item_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['id'] == created_order_item_id

    # 7. Update the created order
    print(f"\nUpdating order with ID: {created_order_id}...")
    update_order_data = {"status": "COMPLETED"}
    response = requests.put(f"{BASE_URL}/orders/{created_order_id}", json=update_order_data)
    print(f"PUT /orders/{created_order_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['status'] == "COMPLETED"

    # 8. Update the created order item
    print(f"\nUpdating order item with ID: {created_order_item_id}...")
    update_order_item_data = {"quantity": 2}
    response = requests.put(f"{BASE_URL}/order_items/{created_order_item_id}", json=update_order_item_data)
    print(f"PUT /order_items/{created_order_item_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['quantity'] == 2

    # 9. Delete the created order item
    print(f"\nDeleting order item with ID: {created_order_item_id}...")
    response = requests.delete(f"{BASE_URL}/order_items/{created_order_item_id}")
    print(f"DELETE /order_items/{created_order_item_id} Status Code: {response.status_code}")
    assert response.status_code == 204

    # Verify order item deletion
    print(f"\nVerifying deletion of order item with ID: {created_order_item_id}...")
    response = requests.get(f"{BASE_URL}/order_items/{created_order_item_id}")
    print(f"GET /order_items/{created_order_item_id} Status Code: {response.status_code}")
    assert response.status_code == 404
    print("Order item deleted successfully.")

    # 10. Delete the created order
    print(f"\nDeleting order with ID: {created_order_id}...")
    response = requests.delete(f"{BASE_URL}/orders/{created_order_id}")
    print(f"DELETE /orders/{created_order_id} Status Code: {response.status_code}")
    assert response.status_code == 204

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
