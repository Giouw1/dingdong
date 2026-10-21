from app.domain.event_bus import  EventBusInterface
from app.infrastructure.inmemoryeventbus import InMemoryEventBus
from app.domain.entities import NotificationPayload
import pytest
# I am testing for a single consumer only, but, even if it was multiple consumers,
#It would create a queue per consumer, so wouldn't change
@pytest.mark.asyncio
async def test_subscribe():
    topic ="user=12345"
    event_bus =  InMemoryEventBus()
    iterator = event_bus.subscribe(topic=topic)
    assert iterator in event_bus._subscribers[topic]

#We are making, in such way that there is a queue per client. Requests would
@pytest.mark.asyncio
async def test_re_subscribe():
    topic ="user=12345"

    event_bus =  InMemoryEventBus()
    iterator = event_bus.subscribe(topic=topic)
    iterator2 = event_bus.subscribe(topic=topic)
    assert iterator != iterator2 
@pytest.mark.asyncio
async def test_publish_topic_nonexistant():
    topic= "user12345"
    data = NotificationPayload(conteudo="vascao",lida=0,timestamp=None)
    event_bus =  InMemoryEventBus()
    await event_bus.publish(topic=topic,data=data)
@pytest.mark.asyncio
async def test_publish_topic():
    topic= "user12345"
    data = NotificationPayload(conteudo="vascao",lida=0, timestamp=None)
    event_bus =  InMemoryEventBus()
    queue = event_bus.subscribe(topic=topic)
    await event_bus.publish(topic=topic,data=data)
    retrieved_data= queue.get_nowait()
    assert data == retrieved_data


