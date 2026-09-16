from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_serves_frontend_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text or "<html" in response.text.lower()
    assert "QR Code" in response.text or "Dashboard" in response.text or "Campainha" in response.text

def test_notify_serves_notify_html():
    response = client.get("/notify")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text or "<html" in response.text.lower()
    assert "Campainha" in response.text or "Tocar" in response.text

def test_notify_with_query_param():
    response = client.get("/notify?nickname=teste_user")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text or "<html" in response.text.lower()

def test_notify_html_alias_serves_same_content():
    response_notify = client.get("/notify")
    response_notify_html = client.get("/notify.html")
    assert response_notify.status_code == 200
    assert response_notify_html.status_code == 200
    assert response_notify.text == response_notify_html.text

def test_nonexistent_frontend_route_returns_404():
    response = client.get("/nonexistent_page.html")
    assert response.status_code == 404

