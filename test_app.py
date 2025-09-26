import json
from app import app

def test_login_success():
    client = app.test_client()
    resp = client.post("/login", json={"username": "miranda", "password": 
"1234"})
    data = json.loads(resp.data)
    assert resp.status_code == 200
    assert "token" in data

def test_login_failure():
    client = app.test_client()
    resp = client.post("/login", json={"username": "wrong", "password": 
"wrong"})
    assert resp.status_code == 401

