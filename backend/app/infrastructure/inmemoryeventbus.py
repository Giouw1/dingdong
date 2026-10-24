from app.domain.event_bus import EventBusInterface
from typing import Dict, AsyncIterator, Any, Set
import asyncio
from app.domain.entities import NotificationPayload, OwnerID
class InMemoryEventBus(EventBusInterface):
    def __init__(self,maxsize:int = 10):
        self._subscribers: Dict[str,Set[asyncio.Queue]] = {}
        self.maxsize = maxsize

    def subscribe(self, topic:str)-> asyncio.Queue:
        if isinstance(topic, OwnerID):
            topic = topic.owner_id
        #For it not to spill RAM
        queue = asyncio.Queue(self.maxsize)

        if topic not in self._subscribers:
            self._subscribers[topic] = set()    
        #This way, I have a queue for every client, and can guarantee each one of them recieves the notificaiton
        self._subscribers[topic].add(queue)
        return queue
    def unsubscribe(self,topic:str,queue:asyncio.Queue)->None:
        if isinstance(topic, OwnerID):
            topic = topic.owner_id
        if topic in self._subscribers:
            self._subscribers[topic].discard(queue)
            # If the user has no more open tabs, remove them from memory
            if not self._subscribers[topic]:
                del self._subscribers[topic]
    #Sync because I don't want to lock the sender, the async part is the SSE motor getting the data.
    def publish(self,topic:str, data:NotificationPayload)-> None:
        if isinstance(topic, OwnerID):
            topic = topic.owner_id
        if topic in self._subscribers:
            for queue in self._subscribers[topic]:
                try:
                    queue.put_nowait(data)
                except asyncio.QueueFull:
                    try:
                        queue.get_nowait()
                        #In case it is all consumed while we are in this block
                    except asyncio.QueueEmpty:
                        pass
                    finally:
                        queue.put_nowait(data) 
        else:
            return
def get_main_event_bus():
    raise NotImplementedError("This dependency must be overridden by the main application.")
