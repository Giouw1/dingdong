from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
import logging
from backend.app.domain.infrastructure_interfaces import AbstractMailboxRepository
from app.domain.entities import OwnerID
from app.infrastructure.opaque_token_repo import OpaqueTokenStore
from hashlib import  md5


#Testes unitários e de integração
def test_register_route(client: TestClient):
    response = client.post("/register", auth=("test_user","securepassword"))
    assert response.status_code == 204
"""
Não é relevante pq o pydantic no fastapi já lida bem
def test_register_route_invalid_credentials(client: TestClient):
    invalid_user_data = {"invalid_field": "data"}
    response = client.post("/register", auth=("test_user"))
    assert response.status_code == 401
"""
def test_login_route_valid_credentials(client: TestClient):
    valid_user_data = {
        "username": "test_user",
        "password": "securepassword",
    }
    
    response = client.post("/login", auth=("test_user","securepassword"))
    assert response.status_code == 401
"""
Não é relevante pq o pydantic no fastapi já lida bem
def test_login_route_invalid_schema(client: TestClient):
    invalid_user_data = {"invalid_field": "data"}
    
    response = client.post("/login", auth=(invalid_user_data))
    assert response.status_code == 401
"""
def test_get_notifications_unauthorized(client: TestClient):
    client.cookies.set(name="session_id", value="1234567890123456789012345678901234567890123" )
    response = client.get("/notifications")
    assert response.status_code == 401
    assert response.json()["detail"] == "User not logged in: session expired."


def test_register_login_integration(client: TestClient, mock_main_mailbox: AbstractMailboxRepository, mock_store:OpaqueTokenStore):
    valid_user_data = {
        "username": "test_user",
        "password": "securepassword",
    }
    
    response = client.post("/register", auth=("test_user","securepassword"))
    assert response.status_code == 204
    response = client.post("/login",auth=("test_user","securepassword"))
    assert mock_store.get_token(opaque_token=response.cookies.get("session_id")) == '1'
    assert response.status_code == 204  

def test_register_login_read_integration(client: TestClient, mock_main_mailbox: AbstractMailboxRepository, mock_store:OpaqueTokenStore):

    response = client.post("/register", auth=("test_user","securepassword"))
    assert response.status_code == 204
    response = client.post("/login",auth=("test_user","securepassword"))
    mock_main_mailbox.save(OwnerID(owner_id='1'),payload=["CRVG"])
    session_id = client.cookies.get("session_id")
    response = client.get("/notifications")
    assert response.json() == [["CRVG"]]


def test_logout(client:TestClient, mock_store:OpaqueTokenStore):
    response = client.post("/register", auth=("test_user","securepassword"))
    assert response.status_code == 204
    response = client.post("/login",auth=("test_user","securepassword"))
    id = client.cookies.get("session_id")
    response = client.post("/logout")
    assert id not in mock_store._tokens
    assert len(client.cookies) == 0
    assert response.status_code == 204


def test_create_nickname_retrieve_valid(client:TestClient):
    response = client.post("/register", auth=("test_user","securepassword"))
    assert response.status_code == 204
    response = client.post("/login",auth=("test_user","securepassword"))
    response = client.post("/nickname/register", params={"Nickname":"Giovanni"})
    assert response.status_code == 204
    response = client.get("/nickname/retrieve")
    assert response.json() == "Giovanni"

def test_change_nickname_retrieve_valid(client:TestClient):
    response = client.post("/register", auth=("test_user","securepassword"))
    assert response.status_code == 204
    response = client.post("/login",auth=("test_user","securepassword"))
    response = client.post("/nickname/change", params={"Nickname":"Giovanni"})
    assert response.status_code == 204
    response = client.get("/nickname/retrieve")
    assert response.json() == "Giovanni"


