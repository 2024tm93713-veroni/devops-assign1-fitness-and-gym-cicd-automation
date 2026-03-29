from app import app


def test_health():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"


def test_programs():
    client = app.test_client()
    resp = client.get("/programs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Fat Loss (FL)" in data


def test_create_client_no_json():
    client = app.test_client()
    response = client.post("/clients", data="invalid")
    assert response.status_code == 400
