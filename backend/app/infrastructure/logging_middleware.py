import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

network_logger = logging.getLogger("network")


class NetworkLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware responsável por interceptar e registrar o tráfego HTTP:
    A ideia é que estruture e lide com os dados da requisição para escrever em um arquivo externo
    - Requests recebidos da rede (Incoming Requests): método, rota, query, versão HTTP e origem.
    - Respostas enviadas pela aplicação (Outgoing Responses): status HTTP retornado e tempo de processamento.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()

        client_host = request.client.host if request.client else "unknown"
        client_port = f":{request.client.port}" if request.client and request.client.port else ""
        client_address = f"{client_host}{client_port}"

        method = request.method
        path = request.url.path
        query = f"?{request.url.query}" if request.url.query else ""
        target = f"{path}{query}"
        http_version = request.scope.get("http_version", "1.1")

        network_logger.info(
            f"Incoming Request: {method} {target} HTTP/{http_version} from {client_address}"
        )

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            network_logger.info(
                f"Outgoing Response: {method} {target} -> Status {response.status_code} ({duration_ms:.2f}ms)"
            )
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            network_logger.error(
                f"Outgoing Response (ERROR): {method} {target} -> Exception: {type(exc).__name__}: {exc} ({duration_ms:.2f}ms)"
            )
            raise exc
