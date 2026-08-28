from app.domain.abstract_usecases import AbstractOwnerUseCases
from app.domain.storage_interfaces import AbstractOwnerRepository, AbstractIDGenerator
from app.domain.storage_interfaces import AbstractMailboxRepository
from app.domain.entities import UserData, NotificationPayload, Nickname, OwnerID
import logging
from typing import List
from pydantic import validate_call, ValidationError
""" 
    Todas as funcionalidades expostas ao cliente dono do mailbox, lida com todo esse lado
"""
class DomainException(Exception): pass
class RegistrationError(DomainException):pass
class AuthenticationError(DomainException):pass
class ResourceNotFoundError(DomainException): pass
class InvalidNickname(DomainException): pass
#Código acoplado ao contrato de Mailbox, OwnerRepo e ID_Generator sendo usado no momento
class OwnerUseCases(AbstractOwnerUseCases):
    def __init__(self, ownermailbox:AbstractOwnerRepository, notifmailbox:AbstractMailboxRepository,id_generator:AbstractIDGenerator):
        self.ownermailbox = ownermailbox
        self.notifmailbox = notifmailbox
        self.id_generator = id_generator

    def register(self, username:str , password:str)->str|RegistrationError:
        id = self.id_generator.generate_id()
        user_data = UserData(username=username,password=password)

        result = self.ownermailbox.register_user(owner_id=id,user_data=user_data) 

        if result == False:
            logging.error(f"Collision in OwnerRepository for username {username}")
            raise RegistrationError("User registration failed: already registered username.")

        result = self.notifmailbox.register_user(id)

        if result == False:
            self.ownermailbox.delete_user(id)
            logging.error(f"Collision in MailboxRepository. Executing rollback for ID {id}")
            raise RegistrationError("Mailbox initialization failed. Registration aborted.")

        return id.owner_id

    def login(self, username:str , password:str)->str|AuthenticationError:

        user_data = UserData(username=username,password=password)

        result = self.ownermailbox.get_user_id(user_data)

        if result == None:
            logging.error(f"There is no such user: {user_data}")
            raise AuthenticationError("User not found")
        
        return result.owner_id
    
    def get_notifications(self, owner_id:str, msg_amount:int=1,offset:int=0)->List|ResourceNotFoundError:

        owner_id = OwnerID(owner_id=owner_id)

        result = self.notifmailbox.get_notifications(target_id=owner_id)
        
        if result == None:
            logging.error(f"Read attempt on non-existent mailbox ID {owner_id}")
            raise ResourceNotFoundError("User not found")
        #Talvez construir o DTO antes de retornar aqui
        return result[offset:offset+msg_amount]
    
    def register_nickname(self,owner_id:str,nickname:str)->bool|RegistrationError:

        owner_id = OwnerID(owner_id=owner_id)
        nickname = Nickname(nickname=nickname)

        result = self.ownermailbox.register_nickname(owner_id=owner_id,nickname=nickname)

        if result == False:
            logging.error(f"User: {owner_id} tried to register already registered nickname: {nickname}")
            raise RegistrationError("There is already such nickname")

        return result
    
    def change_nickname(self,owner_id:str, nickname:str)->str|RegistrationError:

        owner_id = OwnerID(owner_id=owner_id)
        nickname = Nickname(nickname=nickname)

        result = self.ownermailbox.change_nickname(owner_id=owner_id,nickname=nickname)

        if result == False:
            logging.error(f"User: {owner_id} tried to register already registered nickname: {nickname}")
            raise RegistrationError("There is already such nickname")
        
        if result == None:
            logging.error(f"Non-existant User: {owner_id}  tried to register nickname")
            raise ResourceNotFoundError("User not found")
        
        return result

    def retrieve_nickname(self,owner_id:str)->str|ResourceNotFoundError:
        owner_id = OwnerID(owner_id=owner_id)

        result =  self.ownermailbox.get_nickname(owner_id=owner_id)
        if result == None:
            logging.error(f"User: {owner_id} tried to retrieve nickname that does not exist")
            raise ResourceNotFoundError("User has no nickname")
        return result.nickname

    def retrieve_id_by_nickname(self,nickname:str)->str|ResourceNotFoundError:
        nickname = Nickname(nickname=nickname)

        result =  self.ownermailbox.get_user_id_by_nickname(nickname=nickname)
        if result == None:
            raise ResourceNotFoundError("No ID associated to that nickname")
        return result.owner_id

def get_owner_use_cases()->OwnerUseCases:
    raise NotImplementedError("This dependency must be overridden by the main application.")