"""
Tests for authentication endpoints and token verification.
"""
from fastapi import status


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"


def test_login_success(client, test_admin_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_admin_user.email, "password": "SecurePassword123!"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, test_admin_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_admin_user.email, "password": "WrongPassword!"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
