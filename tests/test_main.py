import pytest
import json
import psycopg2
import os

from main import make_app

@pytest.fixture(scope="function")
def app():
    return make_app()

@pytest.fixture(scope="function", autouse=True)
async def setup_teardown_db():
    conn = psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("DB_HOST", "localhost")
    )
    cur = conn.cursor()
    cur.execute("DELETE FROM prices;")
    cur.execute("DELETE FROM drinks;")
    cur.execute("DELETE FROM sizes;")
    conn.commit()
    cur.close()
    conn.close()
    yield
    conn = psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("DB_HOST", "localhost")
    )
    cur = conn.cursor()
    cur.execute("DELETE FROM prices;")
    cur.execute("DELETE FROM drinks;")
    cur.execute("DELETE FROM sizes;")
    conn.commit()
    cur.close()
    conn.close()

async def test_get_drinks(http_client):
    response = await http_client.fetch('http://backend:8888/drinks')
    assert response.code == 200
    data = json.loads(response.body)
    assert isinstance(data, list)

async def test_create_drink(http_client):
    body = {"name": "Test Drink"}
    response = await http_client.fetch('http://backend:8888/drinks', method='POST', body=json.dumps(body))
    assert response.code == 201
    data = json.loads(response.body)
    assert data['name'] == "Test Drink"

async def test_search_drinks(http_client):
    # First, add some drinks to search for
    await http_client.fetch('http://backend:8888/drinks', method='POST', body=json.dumps({"name": "Latte"}))
    await http_client.fetch('http://backend:8888/drinks', method='POST', body=json.dumps({"name": "Cappuccino"}))
    await http_client.fetch('http://backend:8888/drinks', method='POST', body=json.dumps({"name": "Espresso"}))

    response = await http_client.fetch('http://backend:8888/drinks/search?query=latt')
    assert response.code == 200
    data = json.loads(response.body)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "Latte" in [d[1] for d in data]

    response = await http_client.fetch('http://backend:8888/drinks/search?query=capucino') # Fuzzy search
    assert response.code == 200
    data = json.loads(response.body)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "Cappuccino" in [d[1] for d in data]

    response = await http_client.fetch('http://backend:8888/drinks/search?query=') # Test empty query
    assert response.code == 400

    response = await http_client.fetch('http://backend:8888/drinks/search') # Test missing query parameter
    assert response.code == 400