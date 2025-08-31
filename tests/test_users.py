import requests
import json
import time

BASE_URL = "http://127.0.0.1:8880"

def test_users():
    print("\n--- Testing Users ---")

    # First, create a role to associate with the user
    print("Creating a temporary role for user testing...")
    timestamp = str(int(time.time()))
    role_data = {"name": f"TestUserRole_{timestamp}", "description": "Role for testing users"}
    response = requests.post(f"{BASE_URL}/roles", json=role_data)
    assert response.status_code == 201
    test_role_id = response.json()['id']
    print(f"Created Test Role ID: {test_role_id}")

    # 1. Create a new user
    print("\nCreating a new user...")
    new_user_data = {
        "username": f"testuser_{timestamp}",
        "password": "hashedpassword123",
        "firstName": "Test",
        "lastName": "User",
        "email": f"test{timestamp}@example.com",
        "role_id": test_role_id,
        "pin": "1234"
    }
    response = requests.post(f"{BASE_URL}/users", json=new_user_data)
    print(f"POST /users Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    created_user = response.json()
    created_user_id = created_user['data']['id']
    print(f"Created User ID: {created_user_id}")

    # 2. Retrieve all users
    print("\nRetrieving all users...")
    response = requests.get(f"{BASE_URL}/users")
    print(f"GET /users Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert len(response.json()['data']['users']) > 0

    # 3. Retrieve the created user by ID
    print(f"\nRetrieving user with ID: {created_user_id}...")
    response = requests.get(f"{BASE_URL}/users/{created_user_id}")
    print(f"GET /users/{created_user_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['data']['id'] == created_user_id

    # 4. Update the created user
    print(f"\nUpdating user with ID: {created_user_id}...")
    update_data = {"pin": "4321"}
    response = requests.put(f"{BASE_URL}/users/{created_user_id}", json=update_data)
    print(f"PUT /users/{created_user_id} Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    # Pin field is not returned in response for security reasons

    # 5. Delete the created user
    print(f"\nDeleting user with ID: {created_user_id}...")
    response = requests.delete(f"{BASE_URL}/users/{created_user_id}")
    print(f"DELETE /users/{created_user_id} Status Code: {response.status_code}")
    assert response.status_code == 204

    # Verify deletion
    print(f"\nVerifying deletion of user with ID: {created_user_id}...")
    response = requests.get(f"{BASE_URL}/users/{created_user_id}")
    print(f"GET /users/{created_user_id} Status Code: {response.status_code}")
    assert response.status_code == 404
    print("User deleted successfully.")

    # Clean up the temporary role
    print(f"\nDeleting temporary role with ID: {test_role_id}...")
    response = requests.delete(f"{BASE_URL}/roles/{test_role_id}")
    print(f"DELETE /roles/{test_role_id} Status Code: {response.status_code}")
    assert response.status_code == 204
    print("Temporary role deleted successfully.")

    print("\n--- Users Tests Completed ---")

if __name__ == "__main__":
    test_users()
