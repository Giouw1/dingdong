import pytest
from domain.entities import UserData
from domain.storage_interfaces import (
    AbstractMailboxRepository,
    AbstractOwnerRepository,
    AbstractIDGenerator,
)
from owner_path.owner_use_cases import (
    OwnerUseCases,
    AuthenticationError,
    RegistrationError,
    ResourceNotFoundError,
)


# Testes de integração dos processos
def test_register_allvalid(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    result = usecases.register(user_data=userdata)
    assert mock_owner_repo.get_user_id(userdata) is not None
    assert mock_main_mailbox.get_notifications(result) == []
    assert result == '1'


def test_register_allvalid_repeated(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    result = usecases.register(user_data=userdata)
    with pytest.raises(RegistrationError):
        usecases.register(user_data=userdata)

    assert mock_owner_repo.get_user_id(userdata) is not None
    assert mock_main_mailbox.get_notifications(result) == []


# Teste unitário login
def test_login_valid_existing_data(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    resultfirst = usecases.register(user_data=userdata)
    result = usecases.login(user_data=userdata)
    assert result == resultfirst


def test_login_valid_nonexistingdata(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    with pytest.raises(AuthenticationError):
        usecases.login(user_data=userdata)


def test_get_notification(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
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
    userdata = UserData(username="gio", password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    mock_main_mailbox.save(target_id=id, payload=["Hohohohahahohohohahahahah"])
    mock_main_mailbox.save(target_id=id, payload=["CRVG"])
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
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    mock_main_mailbox.save(target_id=id, payload=["Hohohohahahohohohahahahah"])
    mock_main_mailbox.save(target_id=id, payload="CRVG")
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
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    result = usecases.register_nickname(owner_id=id, nickname="CRVG")
    assert mock_owner_repo.get_nickname(id) == "CRVG"
    assert mock_owner_repo.get_user_id_by_nickname("CRVG") == id


def test_register_nickname_repeated_nickname(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    userdata2 = UserData(username="giou", password="vanni")
    usecases.register(user_data=userdata)
    usecases.register(user_data=userdata2)
    id = usecases.login(user_data=userdata)
    id2 = usecases.login(user_data=userdata2)
    usecases.register_nickname(owner_id=id, nickname="CRVG")
    with pytest.raises(RegistrationError):
        usecases.register_nickname(owner_id=id2, nickname="CRVG")
    assert mock_owner_repo.get_nickname(id2) is None


def test_register_nickname_already_registered(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    usecases.register_nickname(owner_id=id, nickname="CRVG")
    result = usecases.register_nickname(owner_id=id, nickname="Vasco")
    assert result == True
    assert mock_owner_repo.get_nickname(id) == "Vasco"


def test_register_nickname_invalidid():
    pass


def test_change_nickname(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    usecases.register_nickname(owner_id=id, nickname="CRVG")
    usecases.change_nickname(owner_id=id, nickname="Vasco")
    assert mock_owner_repo.get_nickname(id) == "Vasco"


def test_change_nickname_repeated_nickname(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    userdata2 = UserData(username="giou", password="vanni")
    usecases.register(user_data=userdata)
    usecases.register(user_data=userdata2)
    id = usecases.login(user_data=userdata)
    id2 = usecases.login(user_data=userdata2)
    usecases.register_nickname(owner_id=id, nickname="CRVG")
    usecases.register_nickname(owner_id=id2, nickname="Vasco")
    with pytest.raises(RegistrationError):
        usecases.change_nickname(owner_id=id2, nickname="CRVG")
    assert mock_owner_repo.get_nickname(id2) == "Vasco"


def test_change_nickname_not_registered(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    result = usecases.change_nickname(owner_id=id, nickname="CRVG")
    assert result == True
    assert mock_owner_repo.get_user_id_by_nickname("CRVG") is not None


def test_change_nickname_invalidid():
    pass


def test_retrieve_nickname(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    usecases.register_nickname(owner_id=id, nickname="CRVG")
    result = usecases.retrieve_nickname(owner_id=id)
    assert result == "CRVG"


def test_retrieve_nickname_nonexistant(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    with pytest.raises(ResourceNotFoundError):
        usecases.retrieve_nickname(owner_id=id)


def test_retrieve_id(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    usecases.register_nickname(owner_id=id, nickname="CRVG")
    result = usecases.retrieve_nickname(owner_id=id)
    assert result == "CRVG"


def test_retrieve_id_nonexistant(
    mock_main_mailbox: AbstractMailboxRepository,
    mock_owner_repo: AbstractOwnerRepository,
    mock_id_generator: AbstractIDGenerator,
):
    usecases = OwnerUseCases(ownermailbox=mock_owner_repo, notifmailbox=mock_main_mailbox, id_generator=mock_id_generator)
    userdata = UserData(username="gio", password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    with pytest.raises(ResourceNotFoundError):
        usecases.retrieve_id_by_nickname(nickname="CRVG")