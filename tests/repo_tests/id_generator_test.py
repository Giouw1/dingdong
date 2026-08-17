from infrastructure.ownerrepo import MockID_Generator, InMemoryOwnerRepo
from domain.entities import OwnerID
def test_generate_id():
    mock_mailbox = InMemoryOwnerRepo()
    generator = MockID_Generator(mock_mailbox)
    id = generator.generate_id()
    assert isinstance(id,str)