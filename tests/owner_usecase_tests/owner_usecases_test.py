from infrastructure.ownerrepo import InMemoryOwnerRepo, MockID_Generator
from infrastructure.mailbox import InMemoryMailbox
from owner_path.owner_use_cases import OwnerUseCases, AuthenticationError,RegistrationError,ResourceNotFoundError
from domain.entities import UserData

import pytest
import logging

#Testes de integração dos processos
def test_register_allvalid():
    mailbox = InMemoryMailbox()
    ownerrepo = InMemoryOwnerRepo()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    result = usecases.register(user_data=userdata)
    assert userdata in ownerrepo.db
    assert ownerrepo.get_user_id(userdata) in mailbox.db
    assert result == '1'

def test_register_allvalid_repeated():
    mailbox = InMemoryMailbox()
    ownerrepo = InMemoryOwnerRepo()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    result = usecases.register(user_data=userdata)
    with pytest.raises(RegistrationError):
        result = usecases.register(user_data=userdata)

    assert userdata in ownerrepo.db
    assert ownerrepo.get_user_id(userdata) in mailbox.db

#Os testes de credencial errada agora estão sendo feitos fora: no gateway. Os casos de uso não contém as validações

#Teste unitário login
def test_login_valid_existing_data():
    mailbox = InMemoryMailbox()
    ownerrepo = InMemoryOwnerRepo()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    resultfirst = usecases.register(user_data=userdata)
    result = usecases.login(user_data=userdata)
    assert result == resultfirst
def test_login_valid_nonexistingdata():
    mailbox = InMemoryMailbox()
    ownerrepo = InMemoryOwnerRepo()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    with pytest.raises(AuthenticationError):
        result = usecases.login(user_data=userdata)

def test_get_notification():
    mailbox = InMemoryMailbox()
    ownerrepo = InMemoryOwnerRepo()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    notif = usecases.get_notifications(id)
    assert notif == []
def test_get_notification_invalidid():        
    mailbox = InMemoryMailbox()
    ownerrepo = InMemoryOwnerRepo()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    with pytest.raises(ResourceNotFoundError):
            notif = usecases.get_notifications(owner_id=1234)
            assert notif == None


#Integração com login e registro
def test_get_notification_properly_readdata():
    mailbox = InMemoryMailbox()
    ownerrepo = InMemoryOwnerRepo()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    mailbox.save(target_id=id,payload=["Hohohohahahohohohahahahah"])
    mailbox.save(target_id=id,payload=["CRVG"])
    notif = usecases.get_notifications(owner_id=id,msg_amount=2)
    assert len(notif) == 2
    assert notif == [["Hohohohahahohohohahahahah"], ["CRVG"]]

def test_get_notification_properly_readdata_with_offset():
    mailbox = InMemoryMailbox()
    ownerrepo = InMemoryOwnerRepo()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    mailbox.save(target_id=id,payload=["Hohohohahahohohohahahahah"])
    mailbox.save(target_id=id,payload="CRVG")
    notif = usecases.get_notifications(owner_id=id,msg_amount=1,offset=1)
    assert len(notif) == 1
    assert notif[0] == "CRVG"

#Por hora os use_cases estão completos, talvez verificar o raise de alguns erros, extra.

def test_register_nickname():
    ownerrepo =  InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    result =usecases.register_nickname(owner_id=id,nickname="CRVG")
    assert ownerrepo.db_id_to_nick[id] == "CRVG"
    assert ownerrepo.db_nick_to_id["CRVG"] == id

def test_register_nickname_repeated_nickname():
    ownerrepo =  InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    userdata2 = UserData(username="giou",password="vanni")
    usecases.register(user_data=userdata)
    usecases.register(user_data=userdata2)
    id = usecases.login(user_data=userdata)
    id2 = usecases.login(user_data=userdata2)
    usecases.register_nickname(owner_id=id,nickname="CRVG")
    with pytest.raises(RegistrationError):
        result = usecases.register_nickname(owner_id=id2,nickname="CRVG")
        assert id2 not in ownerrepo.db_id_to_nick
def test_register_nickname_already_registered():
    ownerrepo =  InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    usecases.register_nickname(owner_id=id,nickname="CRVG")
    result = usecases.register_nickname(owner_id=id,nickname="Vasco")
    assert result == True
    assert ownerrepo.db_id_to_nick[id] == "Vasco"
def test_register_nickname_invalidid():
    pass
#Por enquanto esse teste irá falhar, o repo não está verificando essa integridade referencial
def test_change_nickname():
    ownerrepo =  InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    usecases.register_nickname(owner_id=id,nickname="CRVG")
    usecases.change_nickname(owner_id=id,nickname="Vasco")
    assert ownerrepo.db_id_to_nick[id] == "Vasco"

def test_change_nickname_repeated_nickname():
    ownerrepo =  InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    userdata2 = UserData(username="giou",password="vanni")
    usecases.register(user_data=userdata)
    usecases.register(user_data=userdata2)
    id = usecases.login(user_data=userdata)
    id2 = usecases.login(user_data=userdata2)
    usecases.register_nickname(owner_id=id,nickname="CRVG")
    usecases.register_nickname(owner_id=id2,nickname="Vasco")
    with pytest.raises(RegistrationError):
        result = usecases.change_nickname(owner_id=id2,nickname="CRVG")
        assert ownerrepo.db_id_to_nick[id2] == "Vasco"
def test_change_nickname_not_registered():
    ownerrepo =  InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    result = usecases.change_nickname(owner_id=id,nickname="CRVG")
    assert result == True
    assert "CRVG" in ownerrepo.db_nick_to_id
def test_change_nickname_invalidid():
    pass
#Por enquanto esse teste irá falhar, o repo não está verificando essa integridade referencial

def test_retrieve_nickname():
    ownerrepo =  InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    usecases.register_nickname(owner_id=id,nickname="CRVG")
    result = usecases.retrieve_nickname(owner_id=id)
    assert result == "CRVG"

def test_retrieve_nickname_nonexistant():
    ownerrepo =  InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    with pytest.raises(ResourceNotFoundError):
        result = usecases.retrieve_nickname(owner_id=id)

#Não estou checando os casos do ID não existir no repo de owner, por que, para obter um ID para lidar, precisa efetuar login, e o opaque token lida bem com esse erro.
def test_retrieve_id():
    ownerrepo =  InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    usecases.register_nickname(owner_id=id,nickname="CRVG")
    result = usecases.retrieve_nickname(owner_id=id)
    assert result == "CRVG"
def test_retrieve_id_nonexistant():
    ownerrepo =  InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    mockidgen = MockID_Generator(ownerrepo)
    usecases = OwnerUseCases(ownermailbox=ownerrepo,notifmailbox=mailbox,id_generator=mockidgen)
    userdata = UserData(username="gio",password="vanni")
    usecases.register(user_data=userdata)
    id = usecases.login(user_data=userdata)
    with pytest.raises(ResourceNotFoundError):
        result = usecases.retrieve_id_by_nickname(nickname="CRVG")