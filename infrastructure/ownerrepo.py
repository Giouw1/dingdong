#The idea here is to make repos for two reasons: Username, password, personal data, target id
from typing import Dict, Tuple
from domain.entities import UserData, OwnerID,Nickname
from domain.storage_interfaces import AbstractOwnerRepository,AbstractIDGenerator
import logging
#Lidar com caso owner id não estiver no outro DB, provavelmente algum marcador nesse DB aqui.
#The error names are not that cool
#Not handling mutexes at all: ID Generator needs to be treated better, it is not good as of right now
#Não me parece possível que os ID's sejam comprometidos, ou seja, não estou checando se os ID's de fato
#Existem ao criar nicknames, etc. É algo a se pensar

class InMemoryOwnerRepo(AbstractOwnerRepository):
    def __init__(self):
        self.db :Dict[UserData,int] =  dict()
        self.db_nick_to_id:Dict[Nickname,UserData] = dict()
        self.db_id_to_nick:Dict[UserData,Nickname] = dict()

    def register_user(self, owner_id:int, user_data: UserData)->bool:
        if user_data in self.db:
            return False
        self.db[user_data] = (owner_id)
        return True
    def get_user_id(self,user_data:UserData)-> OwnerID|None:
        if user_data not in self.db:
            return None
        return self.db[user_data]
        
    def delete_user(self, user_data: UserData)->bool:
        if user_data not in self.db:
            return False
        id = self.db[user_data]
        del self.db[user_data]

        if id in self.db_id_to_nick:
            nickname = self.db_id_to_nick[user_data]
            del self.db_id_to_nick[id]
        #Not verifying it here because needs to be true
            del self.db_nick_to_id[nickname]
        return True



#Essa verificação de Owner ID é extremamente lenta. Otimizar isso depois, verifico se o ID existe, mas caro
#Não estou verificando se o ID não existe pois não me parece possível a pessoa injetar um ID zoado aqui
    def register_nickname(self,owner_id:OwnerID,nickname:Nickname)-> bool|None:
        if (nickname in self.db_nick_to_id):
            return False
        if owner_id in self.db_id_to_nick:
            return self.change_nickname(owner_id=owner_id,nickname=nickname)
        else:
            self.db_id_to_nick[owner_id] = nickname
            self.db_nick_to_id[nickname] = owner_id
            return True
        
    def change_nickname(self,owner_id:OwnerID,nickname:Nickname)-> bool|None:
        if owner_id not in self.db_id_to_nick:
            return self.register_nickname(owner_id=owner_id,nickname=nickname)
        if nickname in self.db_nick_to_id:
            return False
        else:
            for key,value in self.db_nick_to_id.items():
                if value == owner_id: 
                    del self.db_nick_to_id[key]
                    break
            self.db_nick_to_id[nickname] = owner_id
            self.db_id_to_nick[owner_id] = nickname
            return True
        
    
    def get_user_id_by_nickname(self,nickname:Nickname)->int|None:
        if nickname not in self.db_nick_to_id:
            return None
        return self.db_nick_to_id[nickname]

    def get_nickname(self,owner_id:OwnerID)->Nickname|None:
        if owner_id in self.db_id_to_nick:
            return self.db_id_to_nick[owner_id]
        else:
            return None
    
class MockID_Generator(AbstractIDGenerator):
    def __init__(self,repository: InMemoryOwnerRepo):
        self.repository = repository
    def generate_id(self)-> OwnerID:
        maxvalue = 0
        for key,value in self.repository.db.items():
            maxvalue = max(int(value),maxvalue)
        return str(maxvalue+1)

def get_owner_repo()->InMemoryOwnerRepo:
    raise NotImplementedError("This dependency must be overridden by the main application.")
def get_id_generator()->MockID_Generator:
    raise NotImplementedError("This dependency must be overridden by the main application.")
