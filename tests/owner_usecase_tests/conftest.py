import pytest
from configs.config import LogSettings,setup_logging, OverallSettings,get_overall_settings
from owner_path.owner_use_cases import OwnerUseCases, get_owner_use_cases
from infrastructure.opaque_token_repo import OpaqueTokenStore, get_opaque_token_store

from owner_path.owner_gateway import router
from infrastructure.ownerrepo import InMemoryOwnerRepo, get_owner_repo, get_id_generator, MockID_Generator
from infrastructure.mailbox import InMemoryMailbox, get_main_mailbox

from fastapi import FastAPI
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def mock_global_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Overrides the global logging configuration dynamically.
    """
    mock_settings = LogSettings(log_level="DEBUG")
    monkeypatch.setattr("configs.config.get_log_settings", lambda: mock_settings)
    setup_logging()

@pytest.fixture
def test_app() -> FastAPI:
    """
    Constructs the FastAPI application and maps the router.
    """
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def mock_main_mailbox() -> InMemoryMailbox:
    return InMemoryMailbox()
@pytest.fixture
def mock_store()->OpaqueTokenStore:
    return OpaqueTokenStore()

@pytest.fixture
def client(test_app: FastAPI,mock_main_mailbox: InMemoryMailbox,mock_store: OpaqueTokenStore) -> TestClient:
    """
    Injects dependencies at the application level and yields a synchronous TestClient.
    """
    mock_owner_repo = InMemoryOwnerRepo()
    mock_id_gen = MockID_Generator(mock_main_mailbox)
    mock_usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox,id_generator=mock_id_gen)
    overallsettings = get_overall_settings()
    test_app.dependency_overrides[get_opaque_token_store] = lambda: mock_store
    test_app.dependency_overrides[get_owner_use_cases] = lambda: mock_usecases
    test_app.dependency_overrides[get_overall_settings] = lambda:overallsettings

    with TestClient(app=test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()


