from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.main import app

from app.config import settings
from app.database import get_db
from app.database import Base
from alembic import command
from unittest.mock import MagicMock


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:testpass@postgres:5432/testdb"


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture 
def test_user(client):
    user_data = {"email": "hello@gmail.com", "password": "password"}
    res = client.post("/users/", json=user_data)
    new_user = res.json()
    new_user['password'] = user_data['password']
    assert res.status_code == 201
    return new_user 

@pytest.fixture(autouse=True)
def mock_kafka_and_valkey(monkeypatch):
    # Mock Kafka producer
    mock_producer_send = MagicMock()
    monkeypatch.setattr("app.kafka.producer.producer.send", mock_producer_send)

    # Mock Valkey client methods
    monkeypatch.setattr("app.valkey.valkey.get", MagicMock(return_value=None))
    monkeypatch.setattr("app.valkey.valkey.setex", MagicMock(return_value=True))
    monkeypatch.setattr("app.valkey.valkey.delete", MagicMock(return_value=True))
    monkeypatch.setattr("app.valkey.valkey.incr", MagicMock(return_value=1))
    monkeypatch.setattr("app.valkey.valkey.expire", MagicMock(return_value=True))

    yield mock_producer_send