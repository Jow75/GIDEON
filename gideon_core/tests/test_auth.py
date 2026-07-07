import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from core.auth import AuthManager, UserRole, DeviceIdentity, AuthError, TokenExpiredError, InvalidTokenError
from api import app
from config.settings import settings
import time
import jwt

client = TestClient(app)

@pytest.fixture(autouse=True)
def enforce_auth():
    """Ensure tests run with auth enabled regardless of local env settings."""
    original = settings.disable_auth_for_dev
    settings.disable_auth_for_dev = False
    yield
    settings.disable_auth_for_dev = original

def test_auth_manager_create_verify():
    device = DeviceIdentity(device_id="test_dev_1", device_type="mobile")
    token = AuthManager.create_access_token(subject="user1", role=UserRole.ADMIN, device=device)
    
    session = AuthManager.verify_token(token)
    assert session.subject == "user1"
    assert session.role == UserRole.ADMIN
    assert session.device.device_id == "test_dev_1"

def test_expired_token():
    # Force an expired token by manually encoding with an old exp
    payload = {
        "sub": "user1",
        "role": UserRole.USER.value,
        "exp": int(time.time()) - 100
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    with pytest.raises(TokenExpiredError):
        AuthManager.verify_token(token)

def test_invalid_signature():
    device = DeviceIdentity(device_id="test", device_type="test")
    token = AuthManager.create_access_token("user1", UserRole.USER, device)
    
    # Modify token to invalidate signature
    invalid_token = token[:-5] + "aaaaa"
    
    with pytest.raises(InvalidTokenError):
        AuthManager.verify_token(invalid_token)

def test_api_missing_token():
    response = client.get("/api/sync")
    assert response.status_code == 401
    assert "Missing or invalid Authorization header" in response.json()["detail"]

def test_api_valid_token():
    device = DeviceIdentity(device_id="test", device_type="test")
    token = AuthManager.create_access_token("user1", UserRole.USER, device)
    
    response = client.get("/api/sync", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_websocket_missing_token():
    with pytest.raises(WebSocketDisconnect) as excinfo:
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_text()
    assert excinfo.value.code == 1008

def test_websocket_valid_token():
    device = DeviceIdentity(device_id="ws_test", device_type="test")
    token = AuthManager.create_access_token("user1", UserRole.USER, device)
    
    with client.websocket_connect(f"/ws?token={token}") as websocket:
        # If it doesn't raise an exception, it connected successfully
        assert True
