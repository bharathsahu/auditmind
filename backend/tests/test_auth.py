from app.services.auth_service import auth_service

def test_hash_password():
    password = "secret_password_123"
    hashed = auth_service.hash_password(password)
    assert hashed != password
    assert auth_service.verify_password(password, hashed) is True

def test_jwt_token_generation_and_decoding():
    payload = {"sub": "auditor_test", "role": "Lead Auditor"}
    token = auth_service.create_access_token(payload)
    assert token is not None

    decoded = auth_service.decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "auditor_test"
    assert decoded["role"] == "Lead Auditor"

def test_login_api_route(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "auditor", "password": "audit123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["username"] == "auditor"
