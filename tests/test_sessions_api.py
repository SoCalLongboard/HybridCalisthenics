def _log(client, date_="2026-01-01", sets=None, form_good=True, notes=None, family="Pushups"):
    return client.post(
        "/api/sessions",
        json={
            "family": family,
            "date": date_,
            "sets": sets or [30, 30],
            "form_good": form_good,
            "notes": notes,
        },
    )


def test_create_session_requires_auth(client):
    resp = _log(client)
    assert resp.status_code == 401


def test_create_session_snapshots_current_exercise_name(auth_client):
    resp = _log(auth_client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["session"]["exercise_name"] == "Wall Pushups"
    assert body["session"]["family"] == "Pushups"


def test_create_session_rejects_unknown_family(auth_client):
    resp = _log(auth_client, family="Nonexistent")
    assert resp.status_code == 422


def test_create_session_rejects_negative_reps(auth_client):
    resp = _log(auth_client, sets=[-5, 10])
    assert resp.status_code == 422


def test_create_session_rejects_invalid_date(auth_client):
    resp = auth_client.post(
        "/api/sessions",
        json={"family": "Pushups", "date": "not-a-date", "sets": [30], "form_good": True},
    )
    assert resp.status_code == 422


def test_list_sessions_filters_by_family(auth_client):
    _log(auth_client, family="Pushups")
    _log(auth_client, family="Squats", sets=[15, 15])
    resp = auth_client.get("/api/sessions", params={"family": "Pushups"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["family"] == "Pushups"


def test_list_sessions_no_filter_returns_all(auth_client):
    _log(auth_client, family="Pushups")
    _log(auth_client, family="Squats", sets=[15, 15])
    resp = auth_client.get("/api/sessions")
    assert len(resp.json()) == 2


def test_patch_session_updates_fields(auth_client):
    create_resp = _log(auth_client)
    session_id = create_resp.json()["session"]["id"]

    resp = auth_client.patch(f"/api/sessions/{session_id}", json={"form_good": False, "notes": "tweaked"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["form_good"] is False
    assert body["notes"] == "tweaked"


def test_delete_session(auth_client):
    create_resp = _log(auth_client)
    session_id = create_resp.json()["session"]["id"]

    resp = auth_client.delete(f"/api/sessions/{session_id}")
    assert resp.status_code == 204

    list_resp = auth_client.get("/api/sessions")
    assert list_resp.json() == []


def test_delete_nonexistent_session_returns_404(auth_client):
    resp = auth_client.delete("/api/sessions/99999")
    assert resp.status_code == 404


def test_patch_nonexistent_session_returns_404(auth_client):
    resp = auth_client.patch("/api/sessions/99999", json={"notes": "x"})
    assert resp.status_code == 404


def test_create_session_returns_caution_on_broken_form(auth_client):
    resp = _log(auth_client, form_good=False)
    assert resp.status_code == 201
    body = resp.json()
    assert body["caution"] is True
    assert "form" in body["caution_reason"]


def test_create_session_no_caution_with_no_prior_history(auth_client):
    resp = _log(auth_client)
    body = resp.json()
    assert body["caution"] is False
    assert body["caution_reason"] is None
