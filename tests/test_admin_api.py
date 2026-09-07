from tests.conftest import make_other_user_client


def _bob(admin_client, db_session):
    bob = make_other_user_client(db_session)
    bob_id = bob.get("/api/auth/me").json()["id"]
    return bob, bob_id


def test_first_registered_user_is_admin(admin_client):
    me = admin_client.get("/api/auth/me").json()
    assert me["is_admin"] is True


def test_second_registered_user_is_not_admin(admin_client, db_session):
    bob, bob_id = _bob(admin_client, db_session)
    assert bob.get("/api/auth/me").json()["is_admin"] is False


def test_non_admin_gets_403_on_admin_routes(admin_client, db_session):
    bob, _ = _bob(admin_client, db_session)
    resp = bob.get("/api/admin/users")
    assert resp.status_code == 403


def test_admin_can_list_users(admin_client, db_session):
    _bob(admin_client, db_session)
    resp = admin_client.get("/api/admin/users")
    assert resp.status_code == 200
    usernames = {u["username"] for u in resp.json()}
    assert usernames == {"admin", "bob"}


def test_disable_blocks_login_and_active_session(admin_client, db_session):
    bob, bob_id = _bob(admin_client, db_session)

    resp = admin_client.post(f"/api/admin/users/{bob_id}/disable")
    assert resp.status_code == 200

    # Already-open session is rejected on the next request.
    assert bob.get("/api/auth/me").status_code == 401

    # Fresh login attempt is rejected too.
    login_resp = bob.post("/api/auth/login", json={"username": "bob", "password": "password123"})
    assert login_resp.status_code == 401


def test_enable_restores_access(admin_client, db_session):
    bob, bob_id = _bob(admin_client, db_session)
    admin_client.post(f"/api/admin/users/{bob_id}/disable")
    admin_client.post(f"/api/admin/users/{bob_id}/enable")

    login_resp = bob.post("/api/auth/login", json={"username": "bob", "password": "password123"})
    assert login_resp.status_code == 200


def test_delete_cascades_progress_and_sessions(admin_client, db_session):
    bob, bob_id = _bob(admin_client, db_session)

    bob.post(
        "/api/sessions",
        json={"family": "Pushups", "date": "2024-01-01", "sets": [5, 5, 5], "form_good": True},
    )

    resp = admin_client.delete(f"/api/admin/users/{bob_id}")
    assert resp.status_code == 204

    from app.models import FamilyProgress, User, WorkoutSession

    assert db_session.get(User, bob_id) is None
    assert db_session.query(WorkoutSession).filter(WorkoutSession.user_id == bob_id).count() == 0
    assert db_session.query(FamilyProgress).filter(FamilyProgress.user_id == bob_id).count() == 0


def test_last_admin_cannot_be_demoted(admin_client):
    admin_id = admin_client.get("/api/auth/me").json()["id"]
    resp = admin_client.post(f"/api/admin/users/{admin_id}/demote")
    assert resp.status_code == 400


def test_last_admin_cannot_be_deleted(admin_client):
    admin_id = admin_client.get("/api/auth/me").json()["id"]
    resp = admin_client.delete(f"/api/admin/users/{admin_id}")
    assert resp.status_code == 400


def test_last_admin_cannot_be_disabled(admin_client):
    admin_id = admin_client.get("/api/auth/me").json()["id"]
    resp = admin_client.post(f"/api/admin/users/{admin_id}/disable")
    assert resp.status_code == 400


def test_admin_cannot_demote_self(admin_client, db_session):
    # even with a second admin present, self-demote is still blocked
    bob, bob_id = _bob(admin_client, db_session)
    admin_client.post(f"/api/admin/users/{bob_id}/promote")
    admin_id = admin_client.get("/api/auth/me").json()["id"]

    resp = admin_client.post(f"/api/admin/users/{admin_id}/demote")
    assert resp.status_code == 400


def test_admin_cannot_delete_self(admin_client, db_session):
    bob, bob_id = _bob(admin_client, db_session)
    admin_client.post(f"/api/admin/users/{bob_id}/promote")
    admin_id = admin_client.get("/api/auth/me").json()["id"]

    resp = admin_client.delete(f"/api/admin/users/{admin_id}")
    assert resp.status_code == 400


def test_admin_cannot_disable_self(admin_client, db_session):
    bob, bob_id = _bob(admin_client, db_session)
    admin_client.post(f"/api/admin/users/{bob_id}/promote")
    admin_id = admin_client.get("/api/auth/me").json()["id"]

    resp = admin_client.post(f"/api/admin/users/{admin_id}/disable")
    assert resp.status_code == 400


def test_promote_demote_with_two_admins(admin_client, db_session):
    bob, bob_id = _bob(admin_client, db_session)
    resp = admin_client.post(f"/api/admin/users/{bob_id}/promote")
    assert resp.status_code == 200
    assert resp.json()["is_admin"] is True

    resp = admin_client.post(f"/api/admin/users/{bob_id}/demote")
    assert resp.status_code == 200
    assert resp.json()["is_admin"] is False


def test_reset_password_forces_change_flow(admin_client, db_session):
    bob, bob_id = _bob(admin_client, db_session)

    resp = admin_client.post(f"/api/admin/users/{bob_id}/reset-password")
    assert resp.status_code == 200
    temp_password = resp.json()["temporary_password"]

    login_resp = bob.post("/api/auth/login", json={"username": "bob", "password": temp_password})
    assert login_resp.status_code == 200
    assert login_resp.json()["must_change_password"] is True

    # Blocked from ordinary app endpoints until the password is changed.
    blocked = bob.get("/api/catalog")
    assert blocked.status_code == 403
    assert blocked.json()["detail"] == "must_change_password"

    # /me and /change-password still work while flagged.
    assert bob.get("/api/auth/me").status_code == 200

    change_resp = bob.post(
        "/api/auth/change-password",
        json={"current_password": temp_password, "new_password": "newpassword123"},
    )
    assert change_resp.status_code == 200
    assert change_resp.json()["must_change_password"] is False

    assert bob.get("/api/catalog").status_code == 200


def test_change_password_requires_correct_current_password(admin_client, db_session):
    bob, bob_id = _bob(admin_client, db_session)
    resp = bob.post(
        "/api/auth/change-password",
        json={"current_password": "wrongpassword", "new_password": "newpassword123"},
    )
    assert resp.status_code == 401
