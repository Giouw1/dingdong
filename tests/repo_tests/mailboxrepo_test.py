from domain.entities import NotificationPayload
from infrastructure.mailbox import InMemoryMailbox
from datetime import datetime
import pytest
import logging

#Por ora, os testes usam o InMemory. Isso pode evoluir com o tempo, é claro, e os testes vão mudar de acordo com a funcionalidade.
def test_registration():
    repo = InMemoryMailbox()
    repo.register_user("vasco")
    assert "vasco" in repo.db
def test_save_validid():
    repo = InMemoryMailbox()
    repo.register_user("vasco")
    time =datetime.now()
    repo.save("vasco",NotificationPayload(conteudo="Ok",lida=False,timestamp=time))
    assert repo.db["vasco"] == [NotificationPayload(conteudo="Ok",lida=False,timestamp=time)]
def test_save_invalidid(caplog):
    repo = InMemoryMailbox()
    result = repo.save("vasco",NotificationPayload(conteudo="Ok",lida=False,timestamp=datetime.now()))
    assert result == False

def test_register_repeatedid(caplog):
    time =datetime.now()
    repo = InMemoryMailbox()
    repo.register_user("vasco")
    repo.save("vasco",NotificationPayload(conteudo="Ok",lida=False,timestamp=time))

    result = repo.register_user("vasco")
    assert result == False
    assert repo.db["vasco"] == [NotificationPayload(conteudo="Ok",lida=False,timestamp=time)]

def test_read_invalidid():
    repo = InMemoryMailbox()
    result = repo.get_notifications("vasco")
    assert result == None


def test_read_validid():
    time =datetime.now()

    repo = InMemoryMailbox()
    repo.register_user("vasco")
    repo.save("vasco",NotificationPayload(conteudo="Ok",lida=False,timestamp=time))
    assert repo.get_notifications("vasco") == [NotificationPayload(conteudo="Ok",lida=False,timestamp=time)]

def test_deletion_validid():
    repo = InMemoryMailbox()
    repo.register_user("vasco")
    repo.delete_user("vasco")
    assert "vasco" not in repo.db
def test_deletion_invalidid():
    repo = InMemoryMailbox()
    result = repo.delete_user("vasco")
    assert result == False



#Não estou testando alguns casos, mas ok.   
#Fazer agora a integração.






