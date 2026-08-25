import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from configs.config import get_overall_settings
from domain.storage_interfaces import (
    AbstractMailboxRepository,
    AbstractOwnerRepository,
    AbstractIDGenerator,
)
from infrastructure.mailbox import InMemoryMailbox
from infrastructure.ownerrepo import InMemoryOwnerRepo, MockID_Generator
from infrastructure.opaque_token_repo import OpaqueTokenStore, get_opaque_token_store
from owner_path.owner_gateway import router
from owner_path.owner_use_cases import OwnerUseCases, get_owner_use_cases


@pytest.fixture
def test_app() -> FastAPI:
    """
    Constructs the FastAPI application and maps the router.
    """
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def mock_owner_repo() -> AbstractOwnerRepository:
    return InMemoryOwnerRepo()


@pytest.fixture
def mock_main_mailbox() -> AbstractMailboxRepository:
    return InMemoryMailbox()


@pytest.fixture
def mock_id_generator(mock_owner_repo: AbstractOwnerRepository) -> AbstractIDGenerator:
    return MockID_Generator(mock_owner_repo)


@pytest.fixture
def mock_store() -> OpaqueTokenStore:
    return OpaqueTokenStore()


@pytest.fixture
def client(
    test_app: FastAPI,
    mock_owner_repo: AbstractOwnerRepository,
    mock_main_mailbox: AbstractMailboxRepository,
    mock_id_generator: AbstractIDGenerator,
    mock_store: OpaqueTokenStore,
) -> TestClient:
    """
    Injects dependencies at the application level and yields a synchronous TestClient.
    """
    mock_usecases = OwnerUseCases(
        ownermailbox=mock_owner_repo,
        notifmailbox=mock_main_mailbox,
        id_generator=mock_id_generator,
    )
    overallsettings = get_overall_settings()
    test_app.dependency_overrides[get_opaque_token_store] = lambda: mock_store
    test_app.dependency_overrides[get_owner_use_cases] = lambda: mock_usecases
    test_app.dependency_overrides[get_overall_settings] = lambda: overallsettings

    with TestClient(app=test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()



