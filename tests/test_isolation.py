from tests.conftest import make_other_user_client


def test_user_cannot_see_other_users_sessions(auth_client, db_session):
    auth_client.post(
        "/api/sessions",
        json={"family": "Pushups", "date": "2026-01-01", "sets": [30, 30], "form_good": True},
    )

    bob = make_other_user_client(db_session)
    resp = bob.get("/api/sessions")
    assert resp.status_code == 200
    assert resp.json() == []


def test_user_cannot_patch_other_users_session(auth_client, db_session):
    create_resp = auth_client.post(
        "/api/sessions",
        json={"family": "Pushups", "date": "2026-01-01", "sets": [30, 30], "form_good": True},
    )
    session_id = create_resp.json()["session"]["id"]

    bob = make_other_user_client(db_session)
    resp = bob.patch(f"/api/sessions/{session_id}", json={"notes": "hijacked"})
    assert resp.status_code == 404


def test_user_cannot_delete_other_users_session(auth_client, db_session):
    create_resp = auth_client.post(
        "/api/sessions",
        json={"family": "Pushups", "date": "2026-01-01", "sets": [30, 30], "form_good": True},
    )
    session_id = create_resp.json()["session"]["id"]

    bob = make_other_user_client(db_session)
    resp = bob.delete(f"/api/sessions/{session_id}")
    assert resp.status_code == 404

    still_there = auth_client.get("/api/sessions")
    assert len(still_there.json()) == 1


def test_users_have_independent_progress(auth_client, db_session):
    auth_client.post(
        "/api/sessions",
        json={"family": "Pushups", "date": "2026-01-01", "sets": [50, 50, 50], "form_good": True},
    )
    auth_client.post(
        "/api/sessions",
        json={"family": "Pushups", "date": "2026-01-02", "sets": [50, 50, 50], "form_good": True},
    )
    auth_client.post("/api/progress/Pushups/advance")

    alice_progress = next(
        f for f in auth_client.get("/api/progress").json()["families"] if f["family"] == "Pushups"
    )
    assert alice_progress["exercise_index"] == 1

    bob = make_other_user_client(db_session)
    bob_progress = next(
        f for f in bob.get("/api/progress").json()["families"] if f["family"] == "Pushups"
    )
    assert bob_progress["exercise_index"] == 0


def test_user_cannot_advance_other_users_progress(auth_client, db_session):
    auth_client.post(
        "/api/sessions",
        json={"family": "Pushups", "date": "2026-01-01", "sets": [50, 50, 50], "form_good": True},
    )
    auth_client.post(
        "/api/sessions",
        json={"family": "Pushups", "date": "2026-01-02", "sets": [50, 50, 50], "form_good": True},
    )

    bob = make_other_user_client(db_session)
    resp = bob.post("/api/progress/Pushups/advance")
    assert resp.status_code == 400

    alice_progress = next(
        f for f in auth_client.get("/api/progress").json()["families"] if f["family"] == "Pushups"
    )
    assert alice_progress["exercise_index"] == 0
