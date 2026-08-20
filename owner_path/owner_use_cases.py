from domain.abstract_usecases import AbstractOwnerUseCases
from domain.storage_interfaces import AbstractOwnerRepository, AbstractIDGenerator
from domain.storage_interfaces import AbstractMailboxRepository
from domain.entities import UserData, NotificationPayload, Nickname, OwnerID
import logging
from typing import List
""" 
    Todas as funcionalidades expostas ao cliente dono do mailbox, lida com todo esse lado
"""
class DomainException(Exception): pass
class RegistrationError(DomainException):pass
class AuthenticationError(DomainException):pass
class ResourceNotFoundError(DomainException): pass
#Código acoplado ao contrato de Mailbox, OwnerRepo e ID_Generator sendo usado no momento
class OwnerUseCases(AbstractOwnerUseCases):
    def __init__(self, ownermailbox:AbstractOwnerRepository, notifmailbox:AbstractMailboxRepository,id_generator:AbstractIDGenerator):
        self.ownermailbox = ownermailbox
        self.notifmailbox = notifmailbox
        self.id_generator = id_generator
    def register(self, user_data:UserData)->int|RegistrationError:
        id = self.id_generator.generate_id()
        result = self.ownermailbox.register_user(owner_id=id,user_data=user_data) 

        if result == False:
            logging.error(f"Collision in OwnerRepository for ID {id}")
            raise RegistrationError("User registration failed due to collision.")

        result = self.notifmailbox.register_user(id)
        if result == False:
            self.ownermailbox.delete_user(id)
            logging.error(f"Collision in MailboxRepository. Executing rollback for ID {id}")
            raise RegistrationError("Mailbox initialization failed. Registration aborted.")

        return id


    def login(self, user_data:UserData)->int|AuthenticationError:
        result = self.ownermailbox.get_user_id(user_data)

        if result == None:
            logging.error("There isn't such User")
            raise AuthenticationError
        
        return result

    def get_notifications(self, owner_id:OwnerID, msg_amount:int=1,offset:int=0)->List[NotificationPayload]|ResourceNotFoundError:
        result = self.notifmailbox.get_notifications(target_id=owner_id)
        
        if result == None:
            logging.error(f"Read attempt on non-existent mailbox ID {owner_id}")
            raise ResourceNotFoundError("There is no such User")
        
        return result[offset:offset+msg_amount]
    

    def register_nickname(self,owner_id:OwnerID,nickname:Nickname)->bool|RegistrationError:
        """
        #Create the nicknames that goes for the public mailbox
        """
        result = self.ownermailbox.register_nickname(owner_id=owner_id,nickname=nickname)
        if result == False:
            raise RegistrationError("There is already such nickname")
        return result
    
    def change_nickname(self,owner_id:OwnerID, nickname:Nickname)->Nickname|RegistrationError:
        result = self.ownermailbox.change_nickname(owner_id=owner_id,nickname=nickname)
        if result == False:
            raise RegistrationError("There is already such nickname")
        if result == None:
            raise ResourceNotFoundError("User not found")
        return result

        """ 
        #Alter nickname

        """
    def retrieve_nickname(self,owner_id:OwnerID)->Nickname|ResourceNotFoundError:

        result =  self.ownermailbox.get_nickname(owner_id=owner_id)
        if result == None:
            raise ResourceNotFoundError("No nickname associated to that ID")
        return result
    def retrieve_id_by_nickname(self,nickname:Nickname)->OwnerID|ResourceNotFoundError:
        result =  self.ownermailbox.get_user_id_by_nickname(nickname=nickname)
        if result == None:
            raise ResourceNotFoundError("No nickname associated to that ID")
        return result

def get_owner_use_cases()->OwnerUseCases:
    raise NotImplementedError("This dependency must be overridden by the main application.")