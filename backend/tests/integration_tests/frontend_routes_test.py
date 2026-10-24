from fastapi.testclient import TestClient
from main import app


def test_root_serves_frontend_html(client:TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text or "<html" in response.text.lower()
    assert "QR Code" in response.text or "Dashboard" in response.text or "Campainha" in response.text

def test_notify_serves_notify_html(client:TestClient):
    response = client.get("/notify")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text or "<html" in response.text.lower()
    assert "Campainha" in response.text or "Tocar" in response.text

def test_notify_with_query_param(client:TestClient):
    response = client.get("/notify?nickname=teste_user")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text or "<html" in response.text.lower()

def test_notify_html_alias_serves_same_content(client:TestClient):
    response_notify = client.get("/notify")
    response_notify_html = client.get("/notify.html")
    assert response_notify.status_code == 200
    assert response_notify_html.status_code == 200
    assert response_notify.text == response_notify_html.text

def test_notified_serves_notified_html(client:TestClient):
    response = client.get("/notified")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Campainha Acionada" in response.text or "notified" in response.text.lower()

def test_notified_html_alias_serves_same_content(client:TestClient):
    response_notified = client.get("/notified")
    response_notified_html = client.get("/notified.html")
    assert response_notified.status_code == 200
    assert response_notified_html.status_code == 200
    assert response_notified.text == response_notified_html.text

def test_nonexistent_frontend_route_returns_404(client:TestClient):
    response = client.get("/nonexistent_page.html")
    assert response.status_code == 404
