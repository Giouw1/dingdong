import pytest
from configs.config import LogSettings, setup_logging
from fastapi import FastAPI
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def mock_global_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Overrides the global logging configuration dynamically.
    """
    mock_settings = LogSettings(log_level="DEBUG")
    monkeypatch.setattr("configs.config.get_log_settings", lambda: mock_settings)
    setup_logging()
@pytest.fixture(autouse=True)
def test_app()-> FastAPI:
    app = FastAPI()
    app.include_router(router) # O router do meu gateway
    return app


@pytest.fixture(autouse=True)
def client(test_app: FastAPI)-> TestClient:
    with TestClient(app=test_app) as test_client:
        yield test_client
