from app.domain.event_bus import EventBusInterface
from typing import Dict, AsyncIterator, Any, Set
import asyncio
from app.domain.entities import NotificationPayload

class InMemoryEventBus(EventBusInterface):
    def __init__(self):
        self._subscribers: Dict[str,Set[asyncio.Queue]] = {}

    def subscribe(self, topic:str)-> asyncio.Queue:
        #For it not to spill RAM
        queue = asyncio.Queue(maxsize=10)

        if topic not in self._subscribers:
            self._subscribers[topic] = set()    
        #This way, I have a queue for every client, and can guarantee each one of them recieves the notificaiton
        self._subscribers[topic].add(queue)
        return queue
    def unsubscribe(self,topic:str,queue:asyncio.Queue)->None:
        if topic in self._subscribers:
            self._subscribers[topic].discard(queue)
            # If the user has no more open tabs, remove them from memory
            if not self._subscribers[topic]:
                del self._subscribers[topic]
    #Async because it has a limit of elements.
    async def publish(self,topic:str, data:NotificationPayload)-> None:
        if topic in self._subscribers:
            for queue in self._subscribers[topic]:
                await queue.put(data)
        else:
            return
        