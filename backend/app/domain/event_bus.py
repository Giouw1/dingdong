from abc import ABC, abstractmethod
import asyncio
from typing import Any, AsyncIterator, Dict, Set

"""I am developing this event bus so that event is processed by each client,
and not by a single one only, as it is the expected behaviour: 
every client interface should be updated, independently of where logged in"""

class EventBusInterface(ABC):
    @abstractmethod
    def __init__(self):
        # Maps user_id -> Set of queues for that user's open connections
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}
    @abstractmethod
    def subscribe(self, topic: str)-> AsyncIterator[any]:
        pass
    @abstractmethod
    def publish(self, topic: str, data: Any)-> None:
        pass

