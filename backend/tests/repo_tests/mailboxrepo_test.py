from datetime import datetime
import pytest
from app.domain.entities import NotificationPayload
from app.domain.storage_interfaces import AbstractMailboxRepository


def test_save_validid(mock_mailbox: AbstractMailboxRepository):
    time = datetime.now()
    payload = NotificationPayload(conteudo="Ok", lida=False, timestamp=time)
    result = mock_mailbox.save("vasco", payload)
    assert result == True
    assert mock_mailbox.get_notifications("vasco") == [payload]


def test_read_invalidid(mock_mailbox: AbstractMailboxRepository):
    result = mock_mailbox.get_notifications("vasco")
    assert result is None


def test_read_validid(mock_mailbox: AbstractMailboxRepository):
    time = datetime.now()
    payload = NotificationPayload(conteudo="Ok", lida=False, timestamp=time)
    mock_mailbox.save("vasco", payload)
    assert mock_mailbox.get_notifications("vasco") == [payload]


def test_deletion_validid(mock_mailbox: AbstractMailboxRepository):
    time = datetime.now()
    payload = NotificationPayload(conteudo="Ok", lida=False, timestamp=time)
    mock_mailbox.save("vasco",payload=payload)
    result = mock_mailbox.delete_user("vasco")
    assert result == True
    assert mock_mailbox.get_notifications("vasco") is None


def test_deletion_invalidid(mock_mailbox: AbstractMailboxRepository):
    result = mock_mailbox.delete_user("vasco")
    assert result == False







