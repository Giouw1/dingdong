import pytest
from fastapi.testclient import TestClient
from main import app
from configs.config import get_env_settings
from app.domain.storage_interfaces import (
    AbstractMailboxRepository,
    AbstractOwnerRepository,
    AbstractIDGenerator,
)
from app.domain.event_bus import EventBusInterface
from app.infrastructure.opaque_token_repo import OpaqueTokenStore, get_opaque_token_store
from app.owner_path.owner_use_cases import OwnerUseCases, get_owner_use_cases
from app.notification_path.notif_use_cases import Notificator_UseCases, get_notifier_use_cases
from app.infrastructure.inmemoryeventbus import get_main_event_bus

@pytest.fixture
def mock_store() -> OpaqueTokenStore:
    return OpaqueTokenStore()

@pytest.fixture
def client(
    mock_owner_repo: AbstractOwnerRepository,
    mock_main_mailbox: AbstractMailboxRepository,
    mock_id_generator: AbstractIDGenerator,
    mock_event_bus: EventBusInterface,
    mock_store: OpaqueTokenStore,
) -> TestClient:
    """
    Injeta dependências limpas e zeradas no app completo do main
    e entrega um TestClient isolado por teste.
    """
    mock_owner_usecases = OwnerUseCases(
        ownermailbox=mock_owner_repo,
        notifmailbox=mock_main_mailbox,
        id_generator=mock_id_generator,
    )
    mock_notif_usecases = Notificator_UseCases(
        ownermailbox=mock_owner_repo,
        notifmailbox=mock_main_mailbox,
        event_bus=mock_event_bus
    )
    overallsettings = get_env_settings()

    app.dependency_overrides[get_opaque_token_store] = lambda: mock_store
    app.dependency_overrides[get_owner_use_cases] = lambda: mock_owner_usecases
    app.dependency_overrides[get_notifier_use_cases] = lambda: mock_notif_usecases
    app.dependency_overrides[get_env_settings] = lambda: overallsettings
    app.dependency_overrides[get_main_event_bus] = lambda: mock_event_bus
    with TestClient(app=app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

import httpx2
import pytest_asyncio

@pytest_asyncio.fixture
async def async_client(client):
    # Uses the same overrides and cookies as your current test client
    transport = httpx2.ASGITransport(app=client.app)
    async with httpx2.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

  