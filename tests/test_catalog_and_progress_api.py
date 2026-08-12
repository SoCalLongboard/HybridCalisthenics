def test_catalog_requires_auth(client):
    resp = client.get("/api/catalog")
    assert resp.status_code == 401


def test_catalog_returns_all_families(auth_client):
    resp = auth_client.get("/api/catalog")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body["families"].keys()) == {
        "Pushups",
        "Leg Raises",
        "Pullups",
        "Squats",
        "Bridges",
        "Twists",
    }
    assert body["schedule"]["monday"] == ["Pushups", "Leg Raises"]
    assert body["schedule"]["sunday"] == []


def test_progress_requires_auth(client):
    resp = client.get("/api/progress")
    assert resp.status_code == 401


def test_progress_fresh_user_all_families_at_index_zero(auth_client):
    resp = auth_client.get("/api/progress")
    assert resp.status_code == 200
    families = resp.json()["families"]
    assert len(families) == 6
    for fam in families:
        assert fam["exercise_index"] == 0
        assert fam["progress_percent"] == 0.0
        assert fam["ready_to_advance"] is False

    pushups = next(f for f in families if f["family"] == "Pushups")
    assert pushups["exercise_name"] == "Wall Pushups"
    assert pushups["total_exercises"] == 11
