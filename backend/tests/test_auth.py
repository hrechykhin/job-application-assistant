def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "secret123", "full_name": "Test User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "secret123"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_login_success(client):
    client.post(
        "/api/v1/auth/register", json={"email": "user@example.com", "password": "mypassword"}
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "user@example.com", "password": "mypassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={"email": "user2@example.com", "password": "correct"})
    response = client.post(
        "/api/v1/auth/login", json={"email": "user2@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_me_endpoint(client):
    client.post("/api/v1/auth/register", json={"email": "me@example.com", "password": "pass123"})
    login = client.post(
        "/api/v1/auth/login", json={"email": "me@example.com", "password": "pass123"}
    )
    token = login.json()["access_token"]
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_me_unauthenticated(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403


def test_refresh_token(client):
    client.post(
        "/api/v1/auth/register", json={"email": "refresh@example.com", "password": "pass123"}
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": "refresh@example.com", "password": "pass123"}
    )
    refresh_token = login.json()["refresh_token"]
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()
