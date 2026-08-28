import pytest
from app.domain.entities import UserData, OwnerID, Nickname
from backend.app.domain.infrastructure_interfaces import (
    AbstractMailboxRepository,
    AbstractOwnerRepository,
    AbstractIDGenerator,
)
from app.owner_path.owner_use_cases import (
    OwnerUseCases,
    AuthenticationError,
    RegistrationError,
    ResourceNotFoundError,
)


def test_register_allvalid(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    result = usecases.register(username="gio", password="vanni")
    assert mock_owner_repo.get_user_id(user_data=UserData(username="gio", password="vanni")) == OwnerID(owner_id="1")
    assert mock_main_mailbox.get_notifications(OwnerID(owner_id=result)) == []
    assert result == '1'


def test_register_allvalid_repeated(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    result = usecases.register(username="gio", password="vanni")
    with pytest.raises(RegistrationError):
        usecases.register(username="gio", password="vanni")

    assert mock_owner_repo.get_user_id(user_data=UserData(username="gio", password="vanni")) is not None
    assert mock_main_mailbox.get_notifications(OwnerID(owner_id=result)) == []


def test_login_valid_existing_data(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    resultfirst = usecases.register(username="gio", password="vanni")
    result = usecases.login(username="gio", password="vanni")
    assert result == resultfirst


def test_login_valid_nonexistingdata(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    with pytest.raises(AuthenticationError):
        usecases.login(username="gio", password="vanni")


def test_get_notification(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    usecases.register(username="gio", password="vanni")
    id = usecases.login(username="gio", password="vanni")
    notif = usecases.get_notifications(id)
    assert notif == []


def test_get_notification_invalidid(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    with pytest.raises(ResourceNotFoundError):
        usecases.get_notifications(owner_id=1234)


# Integração com login e registro
def test_get_notification_properly_readdata(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    usecases.register(username="gio", password="vanni")
    id = usecases.login(username="gio", password="vanni")
    mock_main_mailbox.save(target_id=OwnerID(owner_id=id), payload=["Hohohohahahohohohahahahah"])
    mock_main_mailbox.save(target_id=OwnerID(owner_id=id), payload=["CRVG"])
    notif = usecases.get_notifications(owner_id=id, msg_amount=2)
    assert len(notif) == 2
    assert notif == [["Hohohohahahohohohahahahah"], ["CRVG"]]


def test_get_notification_properly_readdata_with_offset(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(username="gio", password="vanni")
    id = usecases.login(username="gio", password="vanni")
    mock_main_mailbox.save(target_id=OwnerID(owner_id=id), payload=["Hohohohahahohohohahahahah"])
    mock_main_mailbox.save(target_id=OwnerID(owner_id=id), payload="CRVG")
    notif = usecases.get_notifications(owner_id=id, msg_amount=1, offset=1)
    assert len(notif) == 1
    assert notif[0] == "CRVG"


def test_register_nickname(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(username="gio", password="vanni")
    id = usecases.login(username="gio", password="vanni")
    result = usecases.register_nickname(owner_id=id, nickname="CRVG")
    assert mock_owner_repo.get_nickname(OwnerID(owner_id=id)) == Nickname(nickname="CRVG")
    assert mock_owner_repo.get_user_id_by_nickname(nickname=Nickname(nickname="CRVG")) == OwnerID(owner_id=id)


def test_register_nickname_repeated_nickname(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    usecases.register(username="gio", password="vanni")
    usecases.register(username="gio", password="van")
    id = usecases.login(username="gio", password="vanni")
    id2 = usecases.login(username="gio", password="van")
    usecases.register_nickname(owner_id=id, nickname="CRVG")
    with pytest.raises(RegistrationError):
        usecases.register_nickname(owner_id=id2, nickname="CRVG")
    assert mock_owner_repo.get_nickname(OwnerID(owner_id=id2)) is None


def test_register_nickname_already_registered(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(username="gio", password="vanni")
    id = usecases.login(username="gio", password="vanni")
    usecases.register_nickname(owner_id=id, nickname="CRVG")
    result = usecases.register_nickname(owner_id=id, nickname="Vasco")
    assert result == True
    assert mock_owner_repo.get_nickname(OwnerID(owner_id=id)) == Nickname(nickname="Vasco")
"""
def test_register_nickname_none(
        mock_main_mailbox: AbstractMailboxRepository,
        mock_owner_repo: AbstractOwnerRepository,
        mock_id_generator: AbstractIDGenerator,
    ):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    with pytest.raises(RegistrationError):
        result = usecases.register_nickname(owner_id=id, nickname=  None)
    assert None

"""
def test_change_nickname(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(username="gio", password="vanni")
    id = usecases.login(username="gio", password="vanni")
    usecases.register_nickname(owner_id=id, nickname="CRVG")
    usecases.change_nickname(owner_id=id, nickname="Vasco")
    assert mock_owner_repo.get_nickname(OwnerID(owner_id=id)) == Nickname(nickname="Vasco")

def test_change_nickname_repeated_nickname(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    usecases.register(username="gio", password="vanni")
    usecases.register(username="gio", password="van")
    id = usecases.login(username="gio", password="vanni")
    id2 = usecases.login(username="gio", password="van")
    usecases.register_nickname(owner_id=id, nickname="CRVG")
    usecases.register_nickname(owner_id=id2, nickname="Vasco")
    with pytest.raises(RegistrationError):
        usecases.change_nickname(owner_id=id2, nickname="CRVG")
    assert mock_owner_repo.get_nickname(OwnerID(owner_id=id2)) == Nickname(nickname="Vasco")


def test_change_nickname_not_registered(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    usecases.register(username="gio", password="vanni")
    id = usecases.login(username="gio", password="vanni")
    result = usecases.change_nickname(owner_id=id, nickname="CRVG")
    assert result == True
    assert mock_owner_repo.get_user_id_by_nickname(nickname=Nickname(nickname="CRVG")) is not None


def test_retrieve_nickname(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    usecases.register(username="gio", password="vanni")
    id = usecases.login(username="gio", password="vanni")
    usecases.register_nickname(owner_id=id, nickname="CRVG")
    result = usecases.retrieve_nickname(owner_id=id)
    assert result == "CRVG"


def test_retrieve_nickname_nonexistant(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    usecases.register(username="gio", password="vanni")
    id = usecases.login(username="gio", password="vanni")
    with pytest.raises(ResourceNotFoundError):
        usecases.retrieve_nickname(owner_id=id)


def test_retrieve_id(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    usecases.register(username="gio", password="vanni")
    id = usecases.login(username="gio", password="vanni")
    usecases.register_nickname(owner_id=id, nickname="CRVG")
    result = usecases.retrieve_nickname(owner_id=id)
    assert result == "CRVG"


def test_retrieve_id_nonexistant(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    usecases.register(username="gio", password="vanni")
    id = usecases.login(username="gio", password="vanni")
    with pytest.raises(ResourceNotFoundError):
        usecases.retrieve_id_by_nickname(nickname=Nickname(nickname="CRVG"))



