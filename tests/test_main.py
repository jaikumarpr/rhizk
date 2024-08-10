from fastapi.testclient import TestClient
from src.main import app
from src.middlewares.api_key import API_KEY

client = TestClient(app)

def test_public_route():
    response = client.get("/public")
    assert response.status_code == 200
    assert response.json() == {"message": "This is a public route"}

def test_protected_route_with_valid_api_key():
    response = client.get("/protected", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    assert response.json() == {"message": "This is a protected route"}

def test_protected_route_without_api_key():
    response = client.get("/protected")
    assert response.status_code == 403

def test_create_item():
    item = {"name": "Test Item", "description": "This is a test item"}
    response = client.post("/items", json=item, headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    assert response.json()["message"] == "Item created successfully"
    assert response.json()["item"] == item