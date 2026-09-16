from fastapi.testclient import TestClient
from main import app

def test_full_user_flow_end_to_end():
    client = TestClient(app)

    # 1. Owner accesses root HTML page
    response_root = client.get("/")
    assert response_root.status_code == 200
    assert "text/html" in response_root.headers["content-type"]

    # 2. Owner registers
    response_reg = client.post(
        "/owner/register",
        auth=("e2e_user", "e2e_password")
    )
    assert response_reg.status_code == 204

    # 3. Owner logs in and gets session cookie
    response_login = client.post(
        "/owner/login",
        auth=("e2e_user", "e2e_password")
    )
    assert response_login.status_code == 204 or response_login.status_code == 200
    assert "session_id" in response_login.cookies

    # 4. Owner registers nickname
    response_nick_reg = client.post(
        "/owner/nickname/register",
        params={"Nickname": "campainha_e2e"}
    )
    assert response_nick_reg.status_code == 204

    # 5. Owner retrieves nickname
    response_nick_get = client.get("/owner/nickname/retrieve")
    assert response_nick_get.status_code == 200
    assert response_nick_get.json() == "campainha_e2e"

    # 6. Visitor opens notification page via QR code link
    response_notify_page = client.get("/notify", params={"nickname": "campainha_e2e"})
    assert response_notify_page.status_code == 200
    assert "text/html" in response_notify_page.headers["content-type"]

    # 7. Visitor rings doorbell
    response_notif = client.post(
        "/notifications/notificate",
        params={"nickname": "campainha_e2e"},
        json={"payload": "Cheguei no portão!"}
    )
    assert response_notif.status_code == 204

    # 8. Owner checks notifications
    response_notifs = client.get("/owner/notifications", params={"msg_amount": 5})
    assert response_notifs.status_code == 200
    notifs = response_notifs.json()
    assert isinstance(notifs, list)
    assert len(notifs) >= 1
    assert any(n.get("conteudo") == "Cheguei no portão!" for n in notifs)

    # 9. Owner logs out
    response_logout = client.post("/owner/logout")
    assert response_logout.status_code == 204
