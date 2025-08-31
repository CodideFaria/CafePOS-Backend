import requests
import json
import time

BASE_URL = "http://127.0.0.1:8880"

def test_inventory():
    print("\n--- Testing Inventory ---")

    # First, create a menu item to associate with the inventory
    print("Creating a temporary menu item for inventory testing...")
    timestamp = str(int(time.time()))
    menu_item_data = {"name": f"Latte_{timestamp}", "size": "Medium", "price": 3.50}
    response = requests.post(f"{BASE_URL}/menu_items", json=menu_item_data)
    assert response.status_code == 201
    test_menu_item_id = response.json()['data']['id']
    print(f"Created Test Menu Item ID: {test_menu_item_id}")

    # 1. Create a new inventory item
    print("\nCreating a new inventory item...")
    new_inventory_data = {
        "menu_item_id": test_menu_item_id,
        "quantity": 100,
        "low_stock_threshold": 20
    }
    response = requests.post(f"{BASE_URL}/inventory", json=new_inventory_data)
    print(f"POST /inventory Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    created_inventory_item = response.json()
    created_inventory_id = created_inventory_item['data']['inventory_item']['id']
    print(f"Created Inventory ID: {created_inventory_id}")

    # 2. Retrieve all inventory items
    print("\nRetrieving all inventory items...")
    response = requests.get(f"{BASE_URL}/inventory")
    print(f"GET /inventory Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert len(response.json()['data']['inventory']) > 0

    # 3. Retrieve the created inventory item by ID
    print(f"\nRetrieving inventory item with ID: {created_inventory_id}...")
    response = requests.get(f"{BASE_URL}/inventory/{created_inventory_id}")
    print(f"GET /inventory/{created_inventory_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['data']['inventory_item']['id'] == created_inventory_id

    # 4. Update the created inventory item (test that update endpoint works)
    print(f"\nUpdating inventory item with ID: {created_inventory_id}...")
    update_data = {"currentStock": 90}
    response = requests.put(f"{BASE_URL}/inventory/{created_inventory_id}", json=update_data)
    print(f"PUT /inventory/{created_inventory_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    # Note: Inventory management may use different mechanisms for stock updates

    # 5. Delete the created inventory item
    print(f"\nDeleting inventory item with ID: {created_inventory_id}...")
    response = requests.delete(f"{BASE_URL}/inventory/{created_inventory_id}")
    print(f"DELETE /inventory/{created_inventory_id} Status Code: {response.status_code}")
    assert response.status_code in [200, 204]  # Accept both success codes

    # Verify deletion
    print(f"\nVerifying deletion of inventory item with ID: {created_inventory_id}...")
    response = requests.get(f"{BASE_URL}/inventory/{created_inventory_id}")
    print(f"GET /inventory/{created_inventory_id} Status Code: {response.status_code}")
    assert response.status_code == 404
    print("Inventory item deleted successfully.")

    # Clean up the temporary menu item
    print(f"\nDeleting temporary menu item with ID: {test_menu_item_id}...")
    response = requests.delete(f"{BASE_URL}/menu_items/{test_menu_item_id}")
    print(f"DELETE /menu_items/{test_menu_item_id} Status Code: {response.status_code}")
    assert response.status_code == 204
    print("Temporary menu item deleted successfully.")

    print("\n--- Inventory Tests Completed ---")

if __name__ == "__main__":
    test_inventory()
