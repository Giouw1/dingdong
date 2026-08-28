from abc import ABC, abstractmethod
from app.domain.entities import UserData, Nickname, OwnerID, NotificationPayload
from backend.app.domain.infrastructure_interfaces import AbstractOwnerRepository, AbstractMailboxRepository , AbstractIDGenerator
from typing import Union, List
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
    def get_notifications(self,owner_id:int, msg_amount:int, offset:int=0)->Union[List,ResourceNotFoundError]:
        """ 
            Get the notifications
            owner_id:str|int
            mailbox| object 
            number_of_messages: number of messages/notifications to be read
        """
        pass
    @abstractmethod
    def login(self, username=str, password=str)->str|AuthenticationError: 
        """
            Get the ID to handle with the notification mailbox
        """
        pass
    @abstractmethod
    def register(self,username=str, password=str)->str|RegistrationError: 
        """
            Register User in the DB
        """
    @abstractmethod
    def register_nickname(self,owner_id:str,nickname:str)->str|RegistrationError:
        """
        Create the nicknames that goes for the public mailbox
        """
        pass
    @abstractmethod
    def change_nickname(self,owner_id:str, nickname:str)->str|RegistrationError:
        """
        Alter nickname
        """
    @abstractmethod
    def retrieve_nickname(self,owner_id:str)->str|ResourceNotFoundError:
        """Get nickname"""
        pass
    @abstractmethod
    def retrieve_id_by_nickname(self,nickname:str)->str|ResourceNotFoundError:
        pass


class AbstractNotificatorUseCases(ABC):
    @abstractmethod
    def __init__():
        pass
    @abstractmethod
    def notificate()->Union[ResourceNotFoundError,InvalidPayloadError,True]:
        pass