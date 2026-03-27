def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_job(client, register_and_login):
    token = register_and_login()
    job_payload = {
        "company_name": "Acme Corp",
        "title": "Backend Engineer",
        "location": "Berlin, Germany",
        "description": "We are looking for a Python developer...",
    }
    r = client.post("/api/v1/jobs", json=job_payload, headers=_auth_headers(token))
    assert r.status_code == 201
    job = r.json()
    assert job["company_name"] == "Acme Corp"

    r = client.get("/api/v1/jobs", headers=_auth_headers(token))
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_create_application(client, register_and_login):
    token = register_and_login("apps@example.com")
    job = client.post(
        "/api/v1/jobs",
        json={"company_name": "TechCo", "title": "Dev", "description": "Looking for..."},
        headers=_auth_headers(token),
    ).json()

    r = client.post(
        "/api/v1/applications",
        json={"job_id": job["id"]},
        headers=_auth_headers(token),
    )
    assert r.status_code == 201
    assert r.json()["status"] == "SAVED"


def test_update_application_status(client, register_and_login):
    token = register_and_login("status@example.com")
    job = client.post(
        "/api/v1/jobs",
        json={"company_name": "Corp", "title": "Eng", "description": "..."},
        headers=_auth_headers(token),
    ).json()
    app = client.post(
        "/api/v1/applications",
        json={"job_id": job["id"]},
        headers=_auth_headers(token),
    ).json()

    r = client.patch(
        f"/api/v1/applications/{app['id']}",
        json={"status": "APPLIED"},
        headers=_auth_headers(token),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "APPLIED"


def test_application_stats(client, register_and_login):
    token = register_and_login("stats@example.com")
    job = client.post(
        "/api/v1/jobs",
        json={"company_name": "X", "title": "Y", "description": "..."},
        headers=_auth_headers(token),
    ).json()
    client.post("/api/v1/applications", json={"job_id": job["id"]}, headers=_auth_headers(token))

    r = client.get("/api/v1/applications/stats", headers=_auth_headers(token))
    assert r.status_code == 200
    stats = r.json()
    assert stats["total"] == 1
    assert "by_status" in stats
