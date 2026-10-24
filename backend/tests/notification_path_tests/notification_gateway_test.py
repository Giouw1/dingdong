from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from datetime import datetime
from app.domain.entities import NotificationPayload, OwnerID, UserData, Nickname
from app.domain.storage_interfaces import AbstractOwnerRepository, AbstractMailboxRepository
from app.notification_path.notif_use_cases import (
    Notificator_UseCases,
    ResourceNotFoundError,
    InvalidPayloadError,
)
from app.notification_path.notif_gateway import RingDebouncer, get_ring_debouncer

def test_notificate(client: TestClient, mock_main_mailbox: AbstractMailboxRepository, mock_owner_mailbox: AbstractOwnerRepository,notificator_usecases:Notificator_UseCases):
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


def test_ring_success_serves_html_and_no_cache_headers(client: TestClient, mock_main_mailbox: AbstractMailboxRepository, mock_owner_mailbox: AbstractOwnerRepository):
    debouncer = RingDebouncer(cooldown_seconds=3.0)
    client.app.dependency_overrides[get_ring_debouncer] = lambda: debouncer

    omb = mock_owner_mailbox
    omb.register_user(owner_id=2, user_data=UserData("c", "d"))
    omb.register_nickname(owner_id=2, nickname=Nickname(nickname="VisitanteUser"))

    response = client.get("/ring", params={"nickname": "VisitanteUser"})
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "no-store" in response.headers.get("cache-control", "")
    assert "no-cache" in response.headers.get("pragma", "")

    notifications = mock_main_mailbox.get_notifications(target_id=2)
    assert notifications is not None
    assert len(notifications) == 1
    assert "Campainha tocada via QR Code" in notifications[0].conteudo


def test_ring_debouncing_prevents_duplicate_notifications(client: TestClient, mock_main_mailbox: AbstractMailboxRepository, mock_owner_mailbox: AbstractOwnerRepository):
    debouncer = RingDebouncer(cooldown_seconds=5.0)
    client.app.dependency_overrides[get_ring_debouncer] = lambda: debouncer

    omb = mock_owner_mailbox
    omb.register_user(owner_id=3, user_data=UserData("e", "f"))
    omb.register_nickname(owner_id=3, nickname=Nickname(nickname="DebounceUser"))

    # First ring: creates notification
    res1 = client.get("/ring", params={"nickname": "DebounceUser"})
    assert res1.status_code == 200
    assert "X-Ring-Debounced" not in res1.headers

    # Second immediate ring: debounced! (duplicate within cooldown)
    res2 = client.get("/ring", params={"nickname": "DebounceUser"})
    assert res2.status_code == 200
    assert res2.headers.get("x-ring-debounced") == "true"

    # Mailbox should still contain only 1 notification
    notifications = mock_main_mailbox.get_notifications(target_id=3)
    assert len(notifications) == 1


def test_ring_nonexistent_owner_returns_404(client: TestClient):
    response = client.get("/ring", params={"nickname": "GhostUser"})
    assert response.status_code == 404
