from app.domain.event_bus import  EventBusInterface
from app.infrastructure.inmemoryeventbus import InMemoryEventBus
from app.domain.entities import NotificationPayload, OwnerID
import pytest
# I am testing for a single consumer only, but, even if it was multiple consumers,
#It would create a queue per consumer, so wouldn't change
def test_subscribe(mock_event_bus: EventBusInterface):
    topic ="user=12345"
    iterator = mock_event_bus.subscribe(topic=topic)
    assert iterator in mock_event_bus._subscribers[topic]

def test_subscribe_diff_topics_types(mock_event_bus: EventBusInterface):
    topic ="user=12345"
    topic2 = OwnerID(owner_id=topic)
    iterator = mock_event_bus.subscribe(topic=topic)
    iterator2 = mock_event_bus.subscribe(topic=topic2)
    mock_event_bus.publish(topic=topic,data="1")
    assert mock_event_bus._subscribers[topic2.owner_id] == mock_event_bus._subscribers[topic] 
    assert iterator in mock_event_bus._subscribers[topic] and iterator2 in mock_event_bus._subscribers[topic]


#We are making, in such way that there is a queue per client. Requests would
def test_re_subscribe(mock_event_bus: EventBusInterface):
    topic ="user=12345"

    iterator = mock_event_bus.subscribe(topic=topic)
    iterator2 = mock_event_bus.subscribe(topic=topic)
    assert iterator != iterator2 

def test_publish_topic_nonexistant(mock_event_bus: EventBusInterface):
    topic= "user12345"
    data = NotificationPayload(conteudo="vascao",lida=0,timestamp=None)
    mock_event_bus.publish(topic=topic,data=data)

def test_publish_topic(mock_event_bus: EventBusInterface):
    topic= "user12345"
    data = NotificationPayload(conteudo="vascao",lida=0, timestamp=None)
    queue = mock_event_bus.subscribe(topic=topic)
    mock_event_bus.publish(topic=topic,data=data)
    retrieved_data= queue.get_nowait()
    assert data == retrieved_data

def test_publishing_overlimit(mock_event_bus: EventBusInterface):
    topic= "user12345"
    data = NotificationPayload(conteudo="vascao",lida=0, timestamp=None)
    queue = mock_event_bus.subscribe(topic=topic)
    mock_event_bus.publish(topic=topic,data=data)
    retrieved_data= queue.get_nowait()
    assert data == retrieved_data


