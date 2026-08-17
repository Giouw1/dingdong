from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, NewType, Annotated
from pydantic import StringConstraints
from hashlib import sha256
#Falta um formato ao URL post, e não só ao payload.
#A ideia aqui é estabelecer contratos em relação à o que faz parte do nosso funcionamento
@dataclass
class NotificationPayload:
    #Cuidado com esse conteudo string: não estou restringindo o que pode estar aqui dentro,
    #Clássico perigo.
    conteudo: str
    lida: bool 
    #Vou definir que todo payload precisa de um timestamp, mas sem definir "onde" esse timestamp é feito
    timestamp: Optional[datetime]
    
    def to_dict(self):
        """Para permitir armazenagem mais simples e serialização"""
        return{
                "conteudo":self.conteudo,
               "lida":self.lida,
               "timestamp":self.timestamp
               }


#Já que estou usando esse __hash__, cuidado com corrupção de dicionários:
#Pegar o ID e criar um novo UserData com o ID no ownerrepo, ao invés de mudar a chave.
@dataclass(frozen=True)
class UserData:
    #One of both below should be hashed: not sure where it will be done
    username: str
    password: str    
    def to_dict(self):
        """Para permitir armazenagem mais simples e serialização"""
        return{
                "username":self.username,
               "password":self.password
               }
    def __eq__(self, other)-> bool:
        if not isinstance(other, UserData):
            return NotImplemented
        return (self.username == other.username) and (self.password == other.password)
#Já que estou usando esse __hash__, cuidado com corrupção de dicionários:
#Pegar o ID e criar um novo UserData com o ID no ownerrepo, ao invés de mudar a chave.
    def __hash__(self):
        return hash((self.username,self.password))

OwnerIDtype = NewType('OwnerIDtype',str)
Nicknametype = NewType('Nicknametype',str)

OwnerID = Annotated[OwnerIDtype, "To be added constraints"]# Adicionar aqui minhas constraints que forem surgindo
Nickname = Annotated[Nicknametype, "To be added constraints"]


#Não é o ideal o que fiz abaixo, overhead a toa. Usar as primitivas
"""
@dataclass
class OwnerID:
    owner_id: str
    def __hash__(self):
        return hash(self.owner_id)
    def __eq__(self, other)-> bool:
        if isinstance(other, OwnerID):
            return self.owner_id == other.owner_id
        if isinstance(other,str):
            return self.owner_id == other
        return NotImplemented
@dataclass
class Nickname:
    user_nickname: str
    def __hash__(self):
        return hash(self.user_nickname)
    def __eq__(self, other)-> bool:
        if isinstance(other, Nickname):
            return self.user_nickname == other.user_nickname
        if isinstance(other,str):
            return self.user_nickname == other
        return NotImplemented
"""



