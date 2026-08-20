from domain.storage_interfaces import AbstractIDGenerator


def test_generate_id(mock_id_generator: AbstractIDGenerator):
    id = mock_id_generator.generate_id()
    assert isinstance(id, str)