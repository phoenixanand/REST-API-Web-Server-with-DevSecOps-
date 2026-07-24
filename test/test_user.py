from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt
from app.main import app
import pytest
from app import schemas
from app.config import settings
# from .database import client

# client = TestClient(app)

# @pytest.fixture 
# def test_user(client):
#     user_data = {"email": "hello@gmail.com", "password": "password"}
#     res = client.post("/users/", json=user_data)
#     new_user = res.json()
#     new_user['password'] = user_data['password']
#     assert res.status_code == 201
#     return new_user 

# def test_root(client):
#     res = client.get("/")
#     print(res.json().get('message'))
#     assert res.json().get('message') == 'hello world'
    # assert res.status_code == 20

def test_create_user(client):
    res = client.post("/users/", json={"email": "hello@gmail.com", "password": "password"}) 
    new_user = schemas.UserOut(**res.json()) 
    print(res.json())
    assert new_user.email == "hello@gmail.com" 
    assert res.status_code == 201

def test_login_user(test_user, client):
    res = client.post(
        "/login", data={"username": test_user['email'], "password": test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token,
                         settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")
    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', 'password123', 403),
    ('anand@gmail.com', 'wrong_password', 403),
    ('wrongemail@gmail.com', 'wrong_password', 403),
    (None, 'password123', 422),
    ('anand@gmail.com', None, 422)
])


def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post(
        "/login", data={"username": email, "password": password})

    assert res.status_code == status_code