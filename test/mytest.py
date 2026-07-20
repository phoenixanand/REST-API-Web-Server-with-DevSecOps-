from app import schemas
from .database import client, session
import pytest


@pytest.fixture
def test_user(client):
    user_data = {"email": "hello123@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    print(res.json())
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user



# def test_root(client):
#     res = client.get("/")
#     print(res.json().get('message'))
#     assert res.json().get('message') == 'hello world'
#     assert res.status_code == 200


def test_create_user(client):
    res = client.post("/users/", json={"email": "hello123@gmail.com", "password": "password123"})
    new_user = schemas.UserOut(**res.json())
    print(res.json())
    assert new_user.email == "hello123@gmail.com"
    assert res.status_code == 201
    
def test_login_user(test_user, client):
    res = client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
    login_res = schemas.Token(**res.json())
    # payload = 
    assert res.status_code == 200

