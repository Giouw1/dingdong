from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, NewType, Annotated
from pydantic import BaseModel
from hashlib import sha256
class EntityException(Exception): pass
class PayloadBuildError(EntityException): pass

#This one below is built in notif use cases,and is retrieved as whole for the user in the user gateway.
#Not sure if it sure reside besides my core domain, but I am letting it go.
@dataclass
class NotificationPayload:
    conteudo: str
    lida: bool 
    timestamp: Optional[datetime]
    
    def __post_init__(self):
        if len(self.conteudo)>250:
            raise PayloadBuildError("Unsupported payload")



@dataclass(frozen=True)
class UserData:
    username: str
    password: str    
    def __post_init__(self):
        pass
    
@dataclass(frozen=True)
class OwnerID:
    owner_id: str
    def __post_init__(self):
        pass


@dataclass(frozen=True)
class Nickname:
    nickname: str
    def __post_init__(self):
        pass
