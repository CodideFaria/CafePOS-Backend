import pytest
import json
import psycopg2
import os
from decouple import config

from main import make_app

@pytest.fixture(scope="function")
def app():
    return make_app()

@pytest.fixture(scope="function", autouse=True)
async def setup_teardown_db():
    conn = psycopg2.connect(
        dbname=config("POSTGRES_DB"),
        user=config("POSTGRES_USER"),
        password=config("POSTGRES_PASSWORD"),
        host=config("DB_HOST", default="localhost")
    )
    cur = conn.cursor()
    cur.execute("DELETE FROM menu_items WHERE name LIKE 'Test%';")
    conn.commit()
    cur.close()
    conn.close()
    yield
    conn = psycopg2.connect(
        dbname=config("POSTGRES_DB"),
        user=config("POSTGRES_USER"),
        password=config("POSTGRES_PASSWORD"),
        host=config("DB_HOST", default="localhost")
    )
    cur = conn.cursor()
    cur.execute("DELETE FROM menu_items WHERE name LIKE 'Test%';")
    conn.commit()
    cur.close()
    conn.close()

async def test_get_menu_items(http_client):
    response = await http_client.fetch('http://localhost:8880/menu_items')
    assert response.code == 200
    data = json.loads(response.body)
    assert isinstance(data['data']['menu_items'], list)
    assert 'amount' in data['data']

async def test_create_menu_item(http_client):
    body = {"name": "Test Drink", "size": "Medium", "price": 3.50}
    response = await http_client.fetch('http://localhost:8880/menu_items', method='POST', body=json.dumps(body), headers={'Content-Type': 'application/json'})
    assert response.code == 201
    data = json.loads(response.body)
    assert data['data']['name'] == "Test Drink"
    assert data['data']['size'] == "Medium"
    assert data['data']['price'] == 3.50

async def test_menu_items_basic_operations(http_client):
    # Test getting menu items (we know there are items in the database)
    response = await http_client.fetch('http://localhost:8880/menu_items')
    assert response.code == 200
    data = json.loads(response.body)
    assert isinstance(data['data']['menu_items'], list)
    assert len(data['data']['menu_items']) > 0
    assert 'amount' in data['data']
    
    # Check that we have some expected items like "Latte"
    names = [item['name'] for item in data['data']['menu_items']]
    assert any("Latte" in name for name in names)
    
    # Test getting a specific menu item
    if data['data']['menu_items']:
        first_item_id = data['data']['menu_items'][0]['id']
        response = await http_client.fetch(f'http://localhost:8880/menu_items/{first_item_id}')
        assert response.code == 200
        item_data = json.loads(response.body)
        assert 'data' in item_data
        assert item_data['data']['id'] == first_item_id