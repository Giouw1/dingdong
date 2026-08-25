import pytest
from domain.storage_interfaces import (
    AbstractMailboxRepository,
    AbstractOwnerRepository,
    AbstractIDGenerator,
)
from infrastructure.mailbox import InMemoryMailbox
from infrastructure.ownerrepo import InMemoryOwnerRepo, MockID_Generator


@pytest.fixture
def mock_mailbox() -> AbstractMailboxRepository:
    return InMemoryMailbox()


@pytest.fixture
def mock_owner_repo() -> AbstractOwnerRepository:
    return InMemoryOwnerRepo()


@pytest.fixture
def mock_id_generator(mock_owner_repo: AbstractOwnerRepository) -> AbstractIDGenerator:
    return MockID_Generator(mock_owner_repo)
