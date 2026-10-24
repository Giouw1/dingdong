import os
from pathlib import Path
from fastapi.testclient import TestClient
from main import app
from configs.config import get_log_settings, setup_logging


def test_network_logging_records_requests_and_responses(client:TestClient):
    # Garante que o logging esteja configurado
    setup_logging()
    settings = get_log_settings()
    base_dir = Path(__file__).resolve().parent.parent.parent
    log_dir = settings.LOG_DIR if settings.LOG_DIR.is_absolute() else (base_dir / settings.LOG_DIR)
    log_file = log_dir / settings.LOG_FILE

    # Remove o log anterior se existir para um teste limpo
    if log_file.exists():
        # Limpar o arquivo
        with open(log_file, "w", encoding="utf-8") as f:
            f.truncate(0)

    client = TestClient(app)

    # 1. Enviar requisições de teste
    res1 = client.get("/")
    assert res1.status_code == 200

    res2 = client.get("/notify")
    assert res2.status_code == 200

    res3 = client.get("/rota-inexistente")
    assert res3.status_code == 404

    # 2. Verificar que o arquivo de log foi criado
    assert log_file.exists(), f"Log file was not found at {log_file}"

    # 3. Ler o conteúdo do log
    with open(log_file, "r", encoding="utf-8") as f:
        log_content = f.read()

    # 4. Validar que as requisições de entrada e respostas enviadas foram gravadas
    assert "Incoming Request: GET / HTTP/1.1" in log_content
    assert "Outgoing Response: GET / -> Status 200" in log_content

    assert "Incoming Request: GET /notify HTTP/1.1" in log_content
    assert "Outgoing Response: GET /notify -> Status 200" in log_content

    assert "Incoming Request: GET /rota-inexistente HTTP/1.1" in log_content
    assert "Outgoing Response: GET /rota-inexistente -> Status 404" in log_content

    # 5. Validar que a métrica de tempo foi gravada
    assert "ms)" in log_content
