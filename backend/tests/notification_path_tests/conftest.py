import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from notification_path.notif_gateway import notif_router
from notification_path.notif_use_cases import get_notifier_use_cases, Notificator_UseCases
from domain.storage_interfaces import AbstractMailboxRepository, AbstractOwnerRepository
from infrastructure.mailbox import InMemoryMailbox
from infrastructure.ownerrepo import InMemoryOwnerRepo

"""
 The test configuration suite is coupled to the technology used in the server: should change here to test differently
"""

@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(notif_router)  # O router do meu gateway
    return app

@pytest.fixture
def mock_main_mailbox() -> AbstractMailboxRepository:
    return InMemoryMailbox()

@pytest.fixture
def mock_owner_mailbox() -> AbstractOwnerRepository:
    return InMemoryOwnerRepo()

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


