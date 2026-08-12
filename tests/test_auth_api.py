def test_register_success(client):
    resp = client.post("/api/auth/register", json={"username": "alice", "password": "password123"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "alice"
    assert "id" in body


def test_register_duplicate_username(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "password123"})
    resp = client.post("/api/auth/register", json={"username": "alice", "password": "otherpassword"})
    assert resp.status_code == 409


def test_register_password_too_short(client):
    resp = client.post("/api/auth/register", json={"username": "alice", "password": "short"})
    assert resp.status_code == 422


def test_login_success_sets_cookie(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "password123"})
    resp = client.post("/api/auth/login", json={"username": "alice", "password": "password123"})
    assert resp.status_code == 200
    assert "session" in resp.cookies


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "password123"})
    resp = client.post("/api/auth/login", json={"username": "alice", "password": "wrongpassword"})
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post("/api/auth/login", json={"username": "ghost", "password": "password123"})
    assert resp.status_code == 401


def test_me_requires_auth(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(auth_client):
    resp = auth_client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["username"] == "alice"


def test_logout_clears_cookie(auth_client):
    resp = auth_client.post("/api/auth/logout")
    assert resp.status_code == 204
    resp2 = auth_client.get("/api/auth/me")
    assert resp2.status_code == 401


def test_protected_route_rejects_garbage_cookie(client):
    client.cookies.set("session", "not-a-real-token")
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
