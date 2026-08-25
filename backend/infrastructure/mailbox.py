
from domain.storage_interfaces import AbstractMailboxRepository
from domain.entities import NotificationPayload, OwnerID
from pathlib import Path
from typing import Dict,List, Any
import logging


#Por enquanto, usar mailbox na memória ram
#Mudar os log's para serem diferentes dependendo do nível de uso: usuário, dev, etc
class InMemoryMailbox(AbstractMailboxRepository):
    def __init__(self):
        self.db :Dict[str,List[NotificationPayload]] =  dict()
    def save(self,target_id:OwnerID,payload: NotificationPayload)->bool:
        if target_id not in self.db:
            return False
        self.db[target_id].append(payload)
        return True
    def get_notifications(self,target_id:OwnerID)->List[NotificationPayload]|None:
        if target_id not in self.db:
            return None
        return self.db[target_id]
    def register_user(self,target_id:OwnerID)-> bool:
        if target_id in self.db:
            return False
        self.db[target_id] = []
        return True
    def delete_user(self,target_id:OwnerID)-> bool:
        if target_id not in self.db:
            return False
        del self.db[target_id]
        return True

def get_main_mailbox()->InMemoryMailbox:
    raise NotImplementedError("This dependency must be overridden by the main application.")













#Ideias muito para o futuro desse repositório: separar lidas e não lidas em estruturas de dados
#Diferentes.
