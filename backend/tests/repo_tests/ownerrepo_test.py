import pytest
from domain.entities import UserData, OwnerID, Nickname
from domain.storage_interfaces import (
    AbstractOwnerRepository,
    AbstractMailboxRepository,
    AbstractIDGenerator,
)


def test_register_user(
    mock_owner_repo: AbstractOwnerRepository,
    mock_mailbox: AbstractMailboxRepository,
    mock_id_generator: AbstractIDGenerator,
):
    result = mock_owner_repo.register_user(owner_id=mock_id_generator.generate_id(), user_data=UserData("gio", "vanni"))
    assert mock_owner_repo.get_user_id(UserData("gio", "vanni")) is not None
    assert mock_mailbox.get_notifications(mock_owner_repo.get_user_id(UserData("gio", "vanni"))) is None
    assert result == True


def test_register_user_valid_userdata_repeated(
    mock_owner_repo: AbstractOwnerRepository,
    mock_mailbox: AbstractMailboxRepository,
):
    mock_owner_repo.register_user(owner_id=2, user_data=UserData("gio", "vanni"))
    result = mock_owner_repo.register_user(owner_id=1, user_data=UserData("gio", "vanni"))
    assert result == False


def test_delete_user_invalid_user_data(
    mock_owner_repo: AbstractOwnerRepository,
    mock_mailbox: AbstractMailboxRepository,
    mock_id_generator: AbstractIDGenerator,
):
    mock_owner_repo.register_user(owner_id=mock_id_generator.generate_id(), user_data=UserData("gio", "vanni"))
    result = mock_owner_repo.delete_user(user_data=UserData("jão", "vanni"))
    assert result == False


def test_delete_user(
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    mock_owner_repo.register_user(owner_id=mock_id_generator.generate_id(), user_data=UserData("gio", "vanni"))
    result = mock_owner_repo.delete_user(user_data=UserData("gio", "vanni"))
    assert mock_owner_repo.get_user_id(UserData("gio", "vanni")) is None
    assert result == True


def test_retrieve_owner_id_valid(
    mock_owner_repo: AbstractOwnerRepository,
):
    result = mock_owner_repo.register_user(owner_id=1, user_data=UserData("gio", "vanni"))
    assert mock_owner_repo.get_user_id(user_data=UserData("gio", "vanni")) == 1
    assert result == True


def test_retrieve_owner_id_invalid(
    mock_owner_repo: AbstractOwnerRepository,
):
    result = mock_owner_repo.get_user_id(user_data=UserData("gio", "vanni"))
    assert result is None


def test_register_nickname(
    mock_owner_repo: AbstractOwnerRepository,
):
    mock_owner_repo.register_user(0, UserData(username="a", password="b"))
    result = mock_owner_repo.register_nickname(0, nickname="Gio")
    assert mock_owner_repo.get_nickname(0) == "Gio"
    assert mock_owner_repo.get_user_id_by_nickname("Gio") == 0
    assert result == True


def test_register_nickname_repeated_nickname(
    mock_owner_repo: AbstractOwnerRepository,
):
    mock_owner_repo.register_user(0, UserData(username="a", password="b"))
    mock_owner_repo.register_user(1, UserData(username="ab", password="bc"))
    mock_owner_repo.register_nickname(0, nickname="Gio")
    result = mock_owner_repo.register_nickname(1, nickname="Gio")

    assert mock_owner_repo.get_nickname(1) is None
    assert mock_owner_repo.get_user_id_by_nickname("Gio") == 0
    assert result == False


def test_register_nickname_already_registered(
    mock_owner_repo: AbstractOwnerRepository,
):
    mock_owner_repo.register_user(0, UserData(username="a", password="b"))
    mock_owner_repo.register_nickname(0, nickname="Gio")
    result = mock_owner_repo.register_nickname(0, nickname="Go")

    assert mock_owner_repo.get_nickname(0) == "Go"
    assert result == True


def test_change_nickname(
    mock_owner_repo: AbstractOwnerRepository,
):
    mock_owner_repo.register_user(0, UserData(username="a", password="b"))
    mock_owner_repo.register_nickname(0, nickname="Gio")
    result = mock_owner_repo.change_nickname(0, nickname="Go")
    assert result == True
    assert mock_owner_repo.get_user_id_by_nickname("Go") == 0
    assert mock_owner_repo.get_user_id_by_nickname("Gio") is None


def test_change_nickname_alreadyexist(
    mock_owner_repo: AbstractOwnerRepository,
):
    mock_owner_repo.register_user(0, UserData(username="a", password="b"))
    mock_owner_repo.register_user(1, UserData(username="ab", password="bc"))
    mock_owner_repo.register_nickname(0, nickname="Gio")
    mock_owner_repo.register_nickname(1, nickname="Go")
    result = mock_owner_repo.change_nickname(1, nickname="Gio")
    assert mock_owner_repo.get_user_id_by_nickname("Gio") == 0
    assert mock_owner_repo.get_user_id_by_nickname("Go") == 1
    assert result == False
    assert mock_owner_repo.get_nickname(1) == "Go"


def test_change_nickname_notyet_registered(
    mock_owner_repo: AbstractOwnerRepository,
):
    mock_owner_repo.register_user(0, UserData(username="a", password="b"))
    result = mock_owner_repo.change_nickname(0, nickname="Go")
    assert mock_owner_repo.get_nickname(0) == "Go"
    assert mock_owner_repo.get_user_id_by_nickname("Go") == 0
    assert result == True


def test_get_id_by_nickname(
    mock_owner_repo: AbstractOwnerRepository,
):
    mock_owner_repo.register_user(0, UserData(username="a", password="b"))
    mock_owner_repo.register_nickname(0, nickname="Gio")
    result = mock_owner_repo.get_user_id_by_nickname(nickname="Gio")
    assert result == 0


def test_get_id_by_nonexistantnickname(
    mock_owner_repo: AbstractOwnerRepository,
):
    mock_owner_repo.register_user(0, UserData(username="a", password="b"))
    mock_owner_repo.register_nickname(0, nickname="Go")
    result = mock_owner_repo.get_user_id_by_nickname(nickname="Gio")
    assert result is None


def test_get_nick_byid(
    mock_owner_repo: AbstractOwnerRepository,
):
    mock_owner_repo.register_user(0, UserData(username="a", password="b"))
    mock_owner_repo.register_nickname(0, nickname="Gio")
    result = mock_owner_repo.get_nickname(0)
    assert result == "Gio"


def test_get_nickname_by_invalidid(
    mock_owner_repo: AbstractOwnerRepository,
):
    mock_owner_repo.register_user(0, UserData(username="a", password="b"))
    mock_owner_repo.register_nickname(0, nickname="Gio")
    result = mock_owner_repo.get_nickname(1)
    assert result is None


