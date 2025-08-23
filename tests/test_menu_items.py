import requests
import json
import os

BASE_URL = "http://127.0.0.1:8888"

def test_menu_items():
    print("--- Testing Menu Items ---")

    # 1. Create a new menu item
    print("Creating a new menu item...")
    new_item_data = {"name": "Espresso", "size": "Small", "price": "2.50"}
    with open("tests/test_image.png", "rb") as f:
        files = {'image': ('test_image.png', f, 'image/png')}
        response = requests.post(f"{BASE_URL}/menu_items", data=new_item_data, files=files)
    print(f"POST /menu_items Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    created_item = response.json()
    created_item_id = created_item['id']
    print(f"Created Menu Item ID: {created_item_id}")
    assert created_item['image_path'] is not None

    # 2. Retrieve all menu items
    print("\nRetrieving all menu items...")
    response = requests.get(f"{BASE_URL}/menu_items")
    print(f"GET /menu_items Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert len(response.json()['menu_items']) > 0

    # 3. Retrieve the created menu item by ID
    print(f"\nRetrieving menu item with ID: {created_item_id}...")
    response = requests.get(f"{BASE_URL}/menu_items/{created_item_id}")
    print(f"GET /menu_items/{created_item_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['id'] == created_item_id

    # 4. Update the created menu item
    print(f"\nUpdating menu item with ID: {created_item_id}...")
    update_data = {"price": "2.75"}
    response = requests.put(f"{BASE_URL}/menu_items/{created_item_id}", data=update_data)
    print(f"PUT /menu_items/{created_item_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['price'] == 2.75

    # 5. Delete the created menu item
    print(f"\nDeleting menu item with ID: {created_item_id}...")
    response = requests.delete(f"{BASE_URL}/menu_items/{created_item_id}")
    print(f"DELETE /menu_items/{created_item_id} Status Code: {response.status_code}")
    assert response.status_code == 204

    # Verify deletion
    print(f"\nVerifying deletion of menu item with ID: {created_item_id}...")
    response = requests.get(f"{BASE_URL}/menu_items/{created_item_id}")
    print(f"GET /menu_items/{created_item_id} Status Code: {response.status_code}")
    assert response.status_code == 404
    print("Menu item deleted successfully.")

    # Clean up the created image file
    if os.path.exists(created_item['image_path']):
        os.remove(created_item['image_path'])

    print("\n--- Menu Items Tests Completed ---")

if __name__ == "__main__":
    test_menu_items()

