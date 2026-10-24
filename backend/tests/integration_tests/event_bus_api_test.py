import pytest
from fastapi.testclient import TestClient
from main import app
import asyncio
from app.domain.entities import NotificationPayload
from app.owner_path.owner_gateway import notification_event_stream

#Test limit/edge regarding the event bus
    
    
#How I should test it? I should check if a notification arrives in the client gateway.
#So, it should follow the same route of the end to end test, but retrieving from the "stream" gateway, that uses the event bus
@pytest.mark.asyncio
async def test_stream_notifications_e2e(mock_event_bus, mock_store, mock_global_settings):
    # 1. Setup authenticated session for owner "1"
    opaque_token = mock_store.generate_and_store("1")
    # 2. Call the gateway endpoint function directly! (Zero HTTP/Transport deadlocks)
    response = await notification_event_stream(
        opaque_owner_id=opaque_token,
        store=mock_store,
        settings=mock_global_settings,
        event_bus=mock_event_bus
    )
    assert response.status_code == 200
    # 3. Publish to the event bus
    mock_event_bus.publish(
        topic="1",
        data=NotificationPayload(conteudo="Cheguei no portão!", lida=False, timestamp=None)
    )
    # 4. Consume directly from the StreamingResponse generator
    generator = response.body_iterator
    # First chunk is the handshake
    first_chunk = await anext(generator)
    assert ": connected" in first_chunk
    # Second chunk is our notification!
    second_chunk = await anext(generator)
    assert "data:" in second_chunk
    assert "Cheguei no port" in second_chunk
    # 5. Clean teardown
    await generator.aclose()

    
  
  
  
  