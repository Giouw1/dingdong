import pytest
from configs.config import LogSettings,setup_logging
@pytest.fixture(autouse=True)
def mock_global_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Automatically executes before every test.
    Overrides the lru_cache of setup_logging to return a deterministic mock.
    """
    mock_settings = LogSettings(
        log_level="DEBUG",
    )
    # Overrides the setup_logging function to return the mock object
    monkeypatch.setattr("configs.config.get_log_settings", lambda: mock_settings)

    setup_logging()