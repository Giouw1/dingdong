import pytest
from configs.config import LogSettings,setup_logging, get_db_settings, DatabaseSettings, get_env_settings, EnvSettings
from app.domain.storage_interfaces import AbstractIDGenerator,AbstractOwnerRepository,AbstractMailboxRepository
from app.infrastructure.sqlliteownerrepo import SQLite3IDGenerator,SQLite3OwnerRepo
from app.infrastructure.sqllitemailbox import SQLite3Mailbox
from app.infrastructure.inmemorymailbox import InMemoryMailbox
from app.infrastructure.inmemoryownerrepo import InMemoryOwnerRepo, MockID_Generator
from app.domain.abstract_usecases import AbstractHasher
import os
def pytest_configure(config):
    """
    Executa no momento em que o pytest é inicializado, ANTES de qualquer
    módulo de teste ou main.py ser importado.
    """
    os.environ["IN_MEMORY"] = "True"
    os.environ["IS_PRODUCTION"] = "False"
    os.environ["DB_PATH"] = ":memory:"
    # Limpa os caches para garantir que instâncias novas peguem esses valores
    get_db_settings.cache_clear()
    get_env_settings.cache_clear()

@pytest.fixture(autouse=True)
def mock_global_settings(monkeypatch: pytest.MonkeyPatch) -> DatabaseSettings:
    monkeypatch.setenv("IN_MEMORY", "True")
    monkeypatch.setenv("DB_IN_MEMORY", "True")
    monkeypatch.setenv("IS_PRODUCTION", "False")
    repo_mock_settings = DatabaseSettings(
        IN_MEMORY=True,
        DB_PATH=":memory:",
    )
    env_mock_settings = EnvSettings(
        IS_PRODUCTION=False,
    )
    get_db_settings.cache_clear()
    get_env_settings.cache_clear()
    monkeypatch.setattr("configs.config.get_db_settings", lambda: repo_mock_settings)
    monkeypatch.setattr("configs.config.get_env_settings", lambda: env_mock_settings)
    setup_logging()
    return repo_mock_settings


class MockHash(AbstractHasher):
    def __init__(self):
        pass

    def hash(self, text_to_encode: str) -> str:
        return text_to_encode


@pytest.fixture(autouse=True)
def mock_hasher(monkeypatch: pytest.MonkeyPatch) -> None:
    # Overrides the hashing functionality to simplify testing
    monkeypatch.setattr("app.owner_path.owner_use_cases.get_hasher", lambda: MockHash())


@pytest.fixture
def mock_mailbox(mock_global_settings: DatabaseSettings) -> AbstractMailboxRepository:
    if not mock_global_settings.IN_MEMORY:
        return SQLite3Mailbox(db_path=":memory:")
    return InMemoryMailbox()


@pytest.fixture
def mock_main_mailbox(mock_mailbox: AbstractMailboxRepository) -> AbstractMailboxRepository:
    return mock_mailbox


@pytest.fixture
def mock_owner_repo(mock_global_settings: DatabaseSettings) -> AbstractOwnerRepository:
    if not mock_global_settings.IN_MEMORY:
        return SQLite3OwnerRepo(db_path=":memory:")
    return InMemoryOwnerRepo()


@pytest.fixture
def mock_owner_mailbox(mock_owner_repo: AbstractOwnerRepository) -> AbstractOwnerRepository:
    return mock_owner_repo


@pytest.fixture
def mock_id_generator(mock_owner_repo: AbstractOwnerRepository) -> AbstractIDGenerator:
    if isinstance(mock_owner_repo, SQLite3OwnerRepo):
        return SQLite3IDGenerator(repository=mock_owner_repo)
    return MockID_Generator(mock_owner_repo)



