from infrastructure.ownerrepo import InMemoryOwnerRepo, MockID_Generator
from infrastructure.mailbox import InMemoryMailbox
from domain.entities import UserData,OwnerID,Nickname
import pytest
def test_register_user():
    ownerrepo = InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    mockid_generator = MockID_Generator(ownerrepo)
    result = ownerrepo.register_user(owner_id=mockid_generator.generate_id(),user_data=UserData("gio","vanni"))
    assert UserData("gio","vanni") in ownerrepo.db
    assert ownerrepo.get_user_id(UserData("gio","vanni")) not in mailbox.db
    assert result == True

def test_register_user_valid_userdata_repeated():
    ownerrepo = InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    ownerrepo.register_user(owner_id=2,user_data=UserData("gio","vanni"))
    result = ownerrepo.register_user(owner_id=1,user_data=UserData("gio","vanni"))
    
    assert result == False
"""def test_register_used_valid_id_repeated():
    ownerrepo = InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    ownerrepo.register_user(owner_id=1,user_data=UserData("gio","vanni"))
    result = ownerrepo.register_user(owner_id=1,user_data=UserData("gio","vanni"))
    
    assert result == False

Não é necessário no geral por que o registro de ID é interno, mas pode ser algo interessante mais a frente

"""
def test_delete_user_invalid_user_data(caplog):
    ownerrepo = InMemoryOwnerRepo()
    mailbox = InMemoryMailbox()
    mockid_generator = MockID_Generator(ownerrepo)
    ownerrepo.register_user(owner_id=mockid_generator.generate_id(),user_data=UserData("gio","vanni"))
    result = ownerrepo.delete_user(user_data=UserData("jão","vanni"))
    assert result == False

def test_delete_user(caplog):
    ownerrepo = InMemoryOwnerRepo()
    mockid_generator = MockID_Generator(ownerrepo)
    ownerrepo.register_user(owner_id=mockid_generator.generate_id(),user_data=UserData("gio","vanni"))
    result = ownerrepo.delete_user(user_data=UserData("gio","vanni"))
    assert UserData("gio","vanni") not in ownerrepo.db
    assert result == True
    
def test_retrieve_owner_id_valid():
    ownerrepo = InMemoryOwnerRepo()
    result = ownerrepo.register_user(owner_id=1,user_data=UserData("gio","vanni"))
    assert ownerrepo.get_user_id(user_data=UserData("gio","vanni")) == 1
    assert result == True

    
def test_retrieve_owner_id_invalid():
    ownerrepo = InMemoryOwnerRepo()
    result = ownerrepo.get_user_id(user_data=UserData("gio","vanni"))
    assert result == None


def test_register_nickname():
    ownerrepo = InMemoryOwnerRepo()
    ownerrepo.register_user(0,UserData(username="a",password="b"))
    result = ownerrepo.register_nickname(0,nickname="Gio")
    assert 0 in ownerrepo.db_id_to_nick
    assert "Gio" in ownerrepo.db_nick_to_id
    assert result == True


def test_register_nickname_repeated_nickname():
    ownerrepo = InMemoryOwnerRepo()
    ownerrepo.register_user(0,UserData(username="a",password="b"))
    ownerrepo.register_user(1,UserData(username="ab",password="bc"))
    ownerrepo.register_nickname(0,nickname="Gio")
    result = ownerrepo.register_nickname(1,nickname="Gio")

    assert 1 not in ownerrepo.db_id_to_nick
    assert "Gio" in ownerrepo.db_nick_to_id
    assert result == False

#This test also sort of integrates with changing, but we only assert there won't be double nickname
def test_register_nickname_already_registered():
    ownerrepo = InMemoryOwnerRepo()
    ownerrepo.register_user(0,UserData(username="a",password="b"))
    ownerrepo.register_nickname(0,nickname="Gio")
    result = ownerrepo.register_nickname(0,nickname="Go")

    assert 0 in ownerrepo.db_id_to_nick
    assert ownerrepo.db_id_to_nick[0] == "Go"
    assert result == True

def test_change_nickname():
    ownerrepo = InMemoryOwnerRepo()
    ownerrepo.register_user(0,UserData(username="a",password="b"))
    ownerrepo.register_nickname(0,nickname="Gio")
    result = ownerrepo.change_nickname(0,nickname="Go")
    assert result ==True
    assert "Go" in ownerrepo.db_nick_to_id
    assert "Gio" not in ownerrepo.db_nick_to_id
#Mesma coisa que antes, aqui já estou testando mais coisas

def test_change_nickname_alreadyexist():
    ownerrepo = InMemoryOwnerRepo()
    ownerrepo.register_user(0,UserData(username="a",password="b"))
    ownerrepo.register_user(1,UserData(username="ab",password="bc"))
    ownerrepo.register_nickname(0,nickname="Gio")
    ownerrepo.register_nickname(1,nickname="Go")
    result = ownerrepo.change_nickname(1,nickname="Gio")
    assert "Gio" in ownerrepo.db_nick_to_id
    assert "Go" in ownerrepo.db_nick_to_id
    assert result == False
    assert ownerrepo.get_nickname(1) == "Go"

def test_change_nickname_notyet_registered():
    ownerrepo = InMemoryOwnerRepo()
    ownerrepo.register_user(0,UserData(username="a",password="b"))
    result = ownerrepo.change_nickname(0,nickname="Go")
    assert 0 in ownerrepo.db_id_to_nick
    assert "Go" in ownerrepo.db_nick_to_id
    assert result == True


def test_get_id_by_nickname():
    ownerrepo = InMemoryOwnerRepo()
    ownerrepo.register_user(0,UserData(username="a",password="b"))
    ownerrepo.register_nickname(0,nickname="Gio")
    result = ownerrepo.get_user_id_by_nickname(nickname="Gio")
    assert result == 0
def test_get_id_by_nonexistantnickname():
    ownerrepo = InMemoryOwnerRepo()
    ownerrepo.register_user(0,UserData(username="a",password="b"))
    ownerrepo.register_nickname(0,nickname="Go")
    result = ownerrepo.get_user_id_by_nickname(nickname="Gio")
    assert result == None

def test_get_nick_byid():
    ownerrepo = InMemoryOwnerRepo()
    ownerrepo.register_user(0,UserData(username="a",password="b"))
    ownerrepo.register_nickname(0,nickname="Gio")
    result = ownerrepo.get_nickname(0)
    assert result == "Gio"

def test_get_nickname_by_invalidid():
    ownerrepo = InMemoryOwnerRepo()
    ownerrepo.register_user(0,UserData(username="a",password="b"))
    ownerrepo.register_nickname(0,nickname="Gio")
    result = ownerrepo.get_nickname(1)
    assert result == None

