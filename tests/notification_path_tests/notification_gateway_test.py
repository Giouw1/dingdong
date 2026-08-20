from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from datetime import datetime
from domain.entities import NotificationPayload, OwnerID, UserData
from domain.storage_interfaces import AbstractOwnerRepository, AbstractMailboxRepository

def test_notificate(client: TestClient, mock_main_mailbox: AbstractMailboxRepository, mock_owner_mailbox: AbstractOwnerRepository):
    mmb = mock_main_mailbox
    omb = mock_owner_mailbox
    omb.register_user(owner_id=1, user_data=UserData("a", "b"))
    omb.register_nickname(owner_id=1, nickname="Jãovan")
    mmb.register_user(target_id=1)
    nickname = "Jãovan"
    response = client.post("/notificate", params={"nickname": nickname}, json={"payload": "Alguém esteve aqui"})
    notifications = mmb.get_notifications(target_id=1)
    assert notifications is not None
    assert len(notifications) == 1
    assert isinstance(notifications[0], NotificationPayload)
    assert notifications[0].conteudo == "Alguém esteve aqui"
    assert notifications[0].lida is False
    assert response.status_code == 200

def test_notificate_nonexistant_owner(client: TestClient, mock_main_mailbox: AbstractMailboxRepository, mock_owner_mailbox: AbstractOwnerRepository):
    mmb = mock_main_mailbox
    omb = mock_owner_mailbox
    mmb.register_user(target_id=1)
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
