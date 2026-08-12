def _log(client, date_, sets, form_good=True, family="Pushups"):
    return client.post(
        "/api/sessions",
        json={"family": family, "date": date_, "sets": sets, "form_good": form_good},
    )


def _get_family(client, family):
    families = client.get("/api/progress").json()["families"]
    return next(f for f in families if f["family"] == family)


def test_advance_requires_auth(client):
    resp = client.post("/api/progress/Pushups/advance")
    assert resp.status_code == 401


def test_advance_unknown_family(auth_client):
    resp = auth_client.post("/api/progress/Nonexistent/advance")
    assert resp.status_code == 404


def test_advance_rejected_with_no_sessions(auth_client):
    resp = auth_client.post("/api/progress/Pushups/advance")
    assert resp.status_code == 400


def test_ready_flag_true_after_two_qualifying_sessions(auth_client):
    # Wall Pushups level3 = 3 sets of 50
    _log(auth_client, "2026-01-01", [50, 50, 50])
    _log(auth_client, "2026-01-02", [50, 50, 50])

    fam = _get_family(auth_client, "Pushups")
    assert fam["ready_to_advance"] is True


def test_advance_succeeds_and_increments_index(auth_client):
    _log(auth_client, "2026-01-01", [50, 50, 50])
    _log(auth_client, "2026-01-02", [50, 50, 50])

    resp = auth_client.post("/api/progress/Pushups/advance")
    assert resp.status_code == 200
    body = resp.json()
    assert body["exercise_index"] == 1
    assert body["exercise_name"] == "Incline Pushups"

    fam = _get_family(auth_client, "Pushups")
    assert fam["exercise_index"] == 1
    assert fam["exercise_name"] == "Incline Pushups"


def test_advance_server_side_rejects_when_client_would_claim_ready(auth_client):
    # One qualifying, one not -> not ready even though client might assume otherwise
    _log(auth_client, "2026-01-01", [50, 50, 50])
    _log(auth_client, "2026-01-02", [10, 10, 10])

    resp = auth_client.post("/api/progress/Pushups/advance")
    assert resp.status_code == 400

    fam = _get_family(auth_client, "Pushups")
    assert fam["exercise_index"] == 0


def test_readiness_recomputed_live_after_edit(auth_client):
    r1 = _log(auth_client, "2026-01-01", [50, 50, 50])
    r2 = _log(auth_client, "2026-01-02", [10, 10, 10])
    session2_id = r2.json()["session"]["id"]

    assert _get_family(auth_client, "Pushups")["ready_to_advance"] is False

    auth_client.patch(f"/api/sessions/{session2_id}", json={"sets": [50, 50, 50]})

    assert _get_family(auth_client, "Pushups")["ready_to_advance"] is True


def test_readiness_recomputed_live_after_delete(auth_client):
    r1 = _log(auth_client, "2026-01-01", [50, 50, 50])
    r2 = _log(auth_client, "2026-01-02", [50, 50, 50])
    session2_id = r2.json()["session"]["id"]

    assert _get_family(auth_client, "Pushups")["ready_to_advance"] is True

    auth_client.delete(f"/api/sessions/{session2_id}")

    assert _get_family(auth_client, "Pushups")["ready_to_advance"] is False
