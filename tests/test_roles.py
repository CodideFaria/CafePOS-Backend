import requests
import json

BASE_URL = "http://127.0.0.1:8880"

def test_roles():
    print("\n--- Testing Roles ---")

    # 1. Create a new role
    print("Creating a new role (Barista)...")
    new_role_data = {"name": "Barista", "description": "Handles customer orders and prepares drinks."}
    response = requests.post(f"{BASE_URL}/roles", json=new_role_data)
    print(f"POST /roles Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    created_role = response.json()
    created_role_id = created_role['id']
    print(f"Created Role ID: {created_role_id}")

    # 2. Retrieve all roles
    print("\nRetrieving all roles...")
    response = requests.get(f"{BASE_URL}/roles")
    print(f"GET /roles Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert len(response.json()['roles']) > 0

    # 3. Retrieve the created role by ID
    print(f"\nRetrieving role with ID: {created_role_id}...")
    response = requests.get(f"{BASE_URL}/roles/{created_role_id}")
    print(f"GET /roles/{created_role_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['id'] == created_role_id

    # 4. Update the created role
    print(f"\nUpdating role with ID: {created_role_id}...")
    update_data = {"description": "Manages daily operations and staff.", "name": "Manager"}
    response = requests.put(f"{BASE_URL}/roles/{created_role_id}", json=update_data)
    print(f"PUT /roles/{created_role_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['description'] == "Manages daily operations and staff."
    assert response.json()['name'] == "Manager"

    # 5. Delete the created role
    print(f"\nDeleting role with ID: {created_role_id}...")
    response = requests.delete(f"{BASE_URL}/roles/{created_role_id}")
    print(f"DELETE /roles/{created_role_id} Status Code: {response.status_code}")
    assert response.status_code == 204

    # Verify deletion
    print(f"\nVerifying deletion of role with ID: {created_role_id}...")
    response = requests.get(f"{BASE_URL}/roles/{created_role_id}")
    print(f"GET /roles/{created_role_id} Status Code: {response.status_code}")
    assert response.status_code == 404
    print("Role deleted successfully.")

    print("\n--- Roles Tests Completed ---")

if __name__ == "__main__":
    test_roles()
