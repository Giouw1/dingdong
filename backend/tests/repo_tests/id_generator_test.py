from backend.app.domain.infrastructure_interfaces import AbstractIDGenerator
from app.domain.entities import OwnerID

def test_generate_id(mock_id_generator: AbstractIDGenerator):
    id = mock_id_generator.generate_id()
    assert isinstance(id, OwnerID)