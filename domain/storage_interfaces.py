from abc import ABC, abstractmethod
from typing import Dict, Any, List
from domain.entities import Nickname, UserData, OwnerID, NotificationPayload

class AbstractMailboxRepository(ABC):


    @abstractmethod
    def save(self,target_id:OwnerID,payload:NotificationPayload)->bool:

        """Armazenar a notificação em um dado repositório:

            owner_id: [str]
            payload: ????
        
        """
        pass

    @abstractmethod
    def get_notifications(self,target_id:OwnerID)->List[NotificationPayload]|None:

        """Ler as notificações que estão no dado repositório
        
            owner_id: [str]
        
        """
    @abstractmethod
    def register_user(self,target_id:OwnerID)->bool:
        """Registrar o novo usuário
            owner_id: [str]

        
        """
    @abstractmethod
    def delete_user(self,target_id:OwnerID)->bool:
        """"Deleta o dado ID do Mailbox"""


class AbstractOwnerRepository(ABC):
#Vou ter que ver depois colisão de ID's

    @abstractmethod
    def register_user(self, owner_id:OwnerID, user_data:UserData)->bool:
        """ Para registrar, nesse repositório, que contém dados do usuário, um novo usuário
            owner_id: [str]
            user_data

            """

    @abstractmethod
    def delete_user(self,user_data:UserData)->bool|None:
        """Deletar do repositório
        """

    @abstractmethod
    def get_user_id(self,user_data:UserData)->OwnerID|None:
        """Ser capaz de obter o token para pegar as notificações."""

    @abstractmethod
    def register_nickname(self,owner_id:OwnerID,nickname:Nickname)->bool|None:
        "Ser capaz de registrar nickname para expor como campainha"


    @abstractmethod
    def change_nickname(self,owner_id:OwnerID,nickname:Nickname)->bool|None:
        "Ser capaz de trocar o nickname"


    @abstractmethod
    def get_user_id_by_nickname(self,nickname)->OwnerID|None:
        "Ser capaz de retornar o mailbox certo dado o nickname"


    @abstractmethod
    def get_nickname(self,owner_id)->Nickname|None:
        "Return the nickname based on the user_data"

class AbstractIDGenerator(ABC):
    def __init__(self, repository:AbstractOwnerRepository):
        """"Tem que ter uma relação com o DB, para permitir criação"""
    def generate_id(self)->OwnerID:
        """" Gera o ID para o BD"""
    def expose_repo(self):
        """Expôe o repo para testes"""


class OpaqueTokenStore(ABC):
    @abstractmethod
    def __init__(self, capacity: int = 10000) -> None:
        """
        Initializes the OpaqueTokenStore with a strictly bounded LRU cache.
        """
    @abstractmethod
    def generate_and_store(self, backend_token: str,user_data) -> str:
        """
        Generates a secure opaque token, stores the mapping, and enforces 
        the LRU capacity limit.
        """
    @abstractmethod
    def get_token(self, opaque_token: str) -> str: #String-like
        """
        Retrieves the backend token.        
        """
    @abstractmethod
    def get_user_data(self, opaque_token: str) -> str: #String-like
        """
        Retrieves the user data for internal use
        """
    @abstractmethod
    def remove_token(self, opaque_token: str) -> None:
        """
        Explicitly removes a token (e.g., during explicit logout).
        
        Time Complexity: O(1)
        """


