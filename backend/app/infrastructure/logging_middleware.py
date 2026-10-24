import logging
import time
from starlette.requests import Request
from starlette.responses import Response

network_logger = logging.getLogger("network")

class NetworkLoggingMiddleware:
    """
    Pure ASGI Middleware for HTTP logging.
    100% compatible with SSE Streaming, WebSockets, and standard endpoints.
    Zero memory buffering, zero deadlocks.
    """
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        # Only log HTTP requests (pass lifespan and websocket events through)
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        start_time = time.perf_counter()
        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "")
        query = f"?{scope['query_string'].decode()}" if scope.get("query_string") else ""
        target = f"{path}{query}"
        http_version = scope.get("http_version", "1.1")
        client = scope.get("client")
        client_address = f"{client[0]}:{client[1]}" if client else "unknown"
        network_logger.info(
            f"Incoming Request: {method} {target} HTTP/{http_version} from {client_address}"
        )
        # Wrap the ASGI send callable to intercept response status and timing
        async def logging_send(message):
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
                duration_ms = (time.perf_counter() - start_time) * 1000
                network_logger.info(
                    f"Outgoing Response: {method} {target} -> Status {status_code} ({duration_ms:.2f}ms)"
                )
            # Forward the message immediately (no buffering!)
            await send(message)
        try:
            await self.app(scope, receive, logging_send)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            network_logger.error(
                f"Outgoing Response (ERROR): {method} {target} -> Exception: {type(exc).__name__}: {exc} ({duration_ms:.2f}ms)"
            )
            raise exc

  