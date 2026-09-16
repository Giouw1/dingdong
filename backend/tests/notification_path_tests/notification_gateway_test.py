from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from datetime import datetime
from app.domain.entities import NotificationPayload, OwnerID, UserData, Nickname
from app.domain.storage_interfaces import AbstractOwnerRepository, AbstractMailboxRepository

def test_notificate(client: TestClient, mock_main_mailbox: AbstractMailboxRepository, mock_owner_mailbox: AbstractOwnerRepository):
    mmb = mock_main_mailbox
    omb = mock_owner_mailbox
    omb.register_user(owner_id=1, user_data=UserData("a", "b"))
    omb.register_nickname(owner_id=1, nickname=Nickname(nickname="Jãovan"))
    nickname = "Jãovan"
    response = client.post("/notificate", params={"nickname": nickname}, json={"payload": "Alguém esteve aqui"})
    notifications = mmb.get_notifications(target_id=1)
    assert notifications is not None
    assert len(notifications) == 1
    assert isinstance(notifications[0], NotificationPayload)
    assert notifications[0].conteudo == "Alguém esteve aqui"
    assert notifications[0].lida is False
    assert response.status_code == 204

def test_notificate_nonexistant_owner(client: TestClient, mock_main_mailbox: AbstractMailboxRepository, mock_owner_mailbox: AbstractOwnerRepository):
    mmb = mock_main_mailbox
    omb = mock_owner_mailbox
    nickname = "Jãovan"
    response = client.post(url="/notificate", params={"nickname": nickname})
    assert response.status_code == 404

def test_notificate_nonexistant_mailbox(client: TestClient, mock_main_mailbox: AbstractMailboxRepository, mock_owner_mailbox: AbstractOwnerRepository):
    mmb = mock_main_mailbox
    omb = mock_owner_mailbox
    omb.register_user(owner_id=1, user_data=UserData("a", "b"))
    omb.register_nickname(owner_id=1, nickname="Jãovan")
    nickname = "Jãovan"
    response = client.post(url="/notificate", params={"nickname": nickname})
    assert response.status_code == 404

def test_notificate_invalid_payload_type_int(client: TestClient):
    response = client.post("/notificate", params={"nickname": "Jãovan"}, json={"payload": 12345})
    assert response.status_code == 422

def test_notificate_invalid_payload_type_list(client: TestClient):
    response = client.post("/notificate", params={"nickname": "Jãovan"}, json={"payload": ["invalido"]})
    assert response.status_code == 422

def test_notificate_invalid_payload_type_dict(client: TestClient):
    response = client.post("/notificate", params={"nickname": "Jãovan"}, json={"payload": {"chave": "valor"}})
    assert response.status_code == 422

def test_notificate_missing_required_nickname(client: TestClient):
    response = client.post("/notificate", json={"payload": "Alguém esteve aqui"})
    assert response.status_code == 422

