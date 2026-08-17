import secrets
from collections import OrderedDict
from typing import Optional
from domain.entities import UserData,OwnerID
from domain.storage_interfaces import OpaqueTokenStore
class OpaqueTokenStore:
    def __init__(self, capacity: int = 10000) -> None:
        """
        Initializes the OpaqueTokenStore with a strictly bounded LRU cache.
        """
        self.capacity: int = capacity
        self._tokens: OrderedDict[str,OwnerID] = OrderedDict()

    def generate_and_store(self, backend_token: OwnerID) -> str:
        """
        Generates a secure opaque token, stores the mapping, and enforces 
        the LRU capacity limit.
        """
        opaque_token = secrets.token_urlsafe(32)
        
        self._tokens[opaque_token] = backend_token
       
        if len(self._tokens) > self.capacity:
            self._tokens.popitem(last=False)
            
        return opaque_token

    def get_token(self, opaque_token: str) -> Optional[str]:
        """
        Retrieves the backend token.        
        """
        if opaque_token not in self._tokens:
            return None
            
        self._tokens.move_to_end(opaque_token)
        
        return self._tokens[opaque_token]

    def remove_token(self, opaque_token: str) -> bool:
        """
        Explicitly removes a token (e.g., during explicit logout).
        
        Time Complexity: O(1)
        """
        if opaque_token in self._tokens:
            del self._tokens[opaque_token]
            return True
        return False

def get_opaque_token_store()->OpaqueTokenStore:
    raise NotImplementedError("This dependency must be overridden by the main application.")