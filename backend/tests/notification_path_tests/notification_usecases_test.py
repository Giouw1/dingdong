import datetime
import pytest
from domain.entities import NotificationPayload, OwnerID, UserData, Nickname
from domain.storage_interfaces import AbstractMailboxRepository, AbstractOwnerRepository
from notification_path.notif_use_cases import (
    Notificator_UseCases,
    ResourceNotFoundError,
    InvalidPayloadError,
)


def test_valid_save(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_mailbox: AbstractOwnerRepository,
):
    mock_owner_mailbox.register_user(owner_id="1", user_data=UserData(username="Gio", password="Vanni"))
    mock_owner_mailbox.register_nickname(owner_id="1", nickname="vasco")
    mock_main_mailbox.register_user("1")
    notifusecases = Notificator_UseCases(notifmailbox=mock_main_mailbox, ownermailbox=mock_owner_mailbox)
    result = notifusecases.notificate("vasco", payload="Estive aqui")
    assert result is True
    notifications = mock_main_mailbox.get_notifications(target_id="1")
    assert notifications is not None
    assert len(notifications) == 1
    assert notifications[0].conteudo == "Estive aqui"
    assert notifications[0].lida is False
    assert isinstance(notifications[0].timestamp, datetime.datetime)


def test_valid_save_default_payload(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_mailbox: AbstractOwnerRepository,
):
    mock_owner_mailbox.register_user(owner_id="1", user_data=UserData(username="Gio", password="Vanni"))
    mock_owner_mailbox.register_nickname(owner_id="1", nickname="vasco")
    mock_main_mailbox.register_user("1")
    notifusecases = Notificator_UseCases(notifmailbox=mock_main_mailbox, ownermailbox=mock_owner_mailbox)
    result = notifusecases.notificate("vasco", payload=None)
    assert result is True
    notifications = mock_main_mailbox.get_notifications(target_id="1")
    assert notifications is not None
    assert len(notifications) == 1
    assert notifications[0].conteudo.startswith("Notif at")
    assert notifications[0].lida is False


def test_invalid_payload_save(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_mailbox: AbstractOwnerRepository,
):
    mock_owner_mailbox.register_user(owner_id="1", user_data=UserData(username="Gio", password="Vanni"))
    mock_owner_mailbox.register_nickname(owner_id="1", nickname="vasco")
    mock_main_mailbox.register_user("1")
    notifusecases = Notificator_UseCases(notifmailbox=mock_main_mailbox, ownermailbox=mock_owner_mailbox)
    with pytest.raises(InvalidPayloadError):
        notifusecases.notificate("vasco", payload=12345)
    assert mock_main_mailbox.get_notifications("1") == []


def test_nonexistant_user_save(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_mailbox: AbstractOwnerRepository,
):
    notifusecases = Notificator_UseCases(notifmailbox=mock_main_mailbox, ownermailbox=mock_owner_mailbox)
    with pytest.raises(ResourceNotFoundError):
        notifusecases.notificate("vasco", payload="Estive aqui")


def test_nonexistant_mailbox_save(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_mailbox: AbstractOwnerRepository,
):
    mock_owner_mailbox.register_user(owner_id="1", user_data=UserData(username="Gio", password="Vanni"))
    mock_owner_mailbox.register_nickname(owner_id="1", nickname="vasco")
    notifusecases = Notificator_UseCases(notifmailbox=mock_main_mailbox, ownermailbox=mock_owner_mailbox)
    with pytest.raises(ResourceNotFoundError):
        notifusecases.notificate("vasco", payload="Estive aqui")
