import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.notification_path.notif_gateway import notif_router
from app.notification_path.notif_use_cases import get_notifier_use_cases, Notificator_UseCases
from app.domain.storage_interfaces import AbstractMailboxRepository, AbstractOwnerRepository

"""
 The test configuration suite inherits repository fixtures from root conftest.py
"""

@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(notif_router)  # O router do meu gateway
    return app

@pytest.fixture
def client(
    test_app: FastAPI,
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_mailbox: AbstractOwnerRepository,
) -> TestClient:
    test_app.dependency_overrides[get_notifier_use_cases] = lambda: Notificator_UseCases(
        ownermailbox=mock_owner_mailbox, notifmailbox=mock_main_mailbox
    )
    with TestClient(app=test_app) as test_client:
        yield test_client
    test_app.dependency_overrides.clear()


