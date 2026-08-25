from abc import ABC, abstractmethod
from domain.entities import UserData, Nickname, OwnerID
from domain.storage_interfaces import AbstractOwnerRepository, AbstractMailboxRepository , AbstractIDGenerator
from typing import Union
"""
    A ideia é que esse Gateway vai receber as requisições do usuário de REGISTRAR, LOGAR, LER
    E esse OwnerUse Cases vai acoplar o Gateway à implementação do mailbox.
"""
class DomainException(Exception): pass
class RegistrationError(DomainException):pass
class AuthenticationError(DomainException):pass
class ResourceNotFoundError(DomainException): pass
class InvalidPayloadError(DomainException): pass

class AbstractOwnerUseCases(ABC):
    @abstractmethod
    def __init__(self,ownermailbox:AbstractOwnerRepository,notifmailbox:AbstractMailboxRepository, id_generator: AbstractIDGenerator):
        """
        Initializes the usecases framework
        """
        pass
    @abstractmethod
    def get_notifications(self,owner_id:int, msg_amount:int, offset:int=0):
        """ 
            Get the notifications
            owner_id:str|int
            mailbox| object 
            number_of_messages: number of messages/notifications to be read
        """
        pass
    @abstractmethod
    def login(self, UserData: UserData)->OwnerID|AuthenticationError: 
        """
            Get the ID to handle with the notification mailbox
        """
        pass
    @abstractmethod
    def register(self,UserData: UserData)->OwnerID|RegistrationError: 
        """
            Register User in the DB
        """
    @abstractmethod
    def register_nickname(self,owner_id:OwnerID,nickname:Nickname)->Nickname|RegistrationError:
        """
        Create the nicknames that goes for the public mailbox
        """
        pass
    @abstractmethod
    def change_nickname(self,owner_id:OwnerID, nickname:Nickname)->Nickname|RegistrationError:
        """
        Alter nickname
        """
    @abstractmethod
    def retrieve_nickname(self,owner_id:OwnerID)->Nickname|ResourceNotFoundError:
        """Get nickname"""
        pass
    @abstractmethod
    def retrieve_id_by_nickname(self,nickname:Nickname)->OwnerID|ResourceNotFoundError:
        pass


class AbstractNotificatorUseCases(ABC):
    @abstractmethod
    def __init__():
        pass
    @abstractmethod
    def notificate()->Union[ResourceNotFoundError,InvalidPayloadError,True]:
        pass