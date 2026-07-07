"""
RC1 Validation Suite — VP1: Deployment Validation
Tests that the API boots correctly, health probes respond, and the startup
configuration validation logic works as expected.
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a fresh TestClient for each test.
    We import the app inside the fixture so settings patches take effect."""
    from api import app
    return TestClient(app, raise_server_exceptions=False)


# ─── Health Endpoints ───────────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "version" in body

    def test_liveness_returns_alive(self, client):
        response = client.get("/liveness")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    def test_readiness_reflects_core_state(self, client):
        """Readiness should return 200 if core initialised, 503 otherwise."""
        response = client.get("/readiness")
        # In test environment the core *may* fail to init (no NVIDIA key etc),
        # but we should always get either 200 or 503, never 500.
        assert response.status_code in (200, 503)


# ─── Configuration Validation ────────────────────────────────────────────────

class TestConfigValidation:
    @pytest.mark.asyncio
    async def test_production_rejects_default_jwt_secret(self):
        """In production, the default JWT secret must cause a startup failure."""
        from config.settings import settings
        original_env = settings.environment
        original_auth = settings.disable_auth_for_dev
        original_secret = settings.jwt_secret

        try:
            settings.environment = "production"
            settings.disable_auth_for_dev = False
            settings.jwt_secret = "default_jwt_secret_change_in_production"

            from api import app, lifespan
            with pytest.raises(RuntimeError):
                async with lifespan(app):
                    pass
        finally:
            settings.environment = original_env
            settings.disable_auth_for_dev = original_auth
            settings.jwt_secret = original_secret

    @pytest.mark.asyncio
    async def test_invalid_redis_url_rejected(self):
        """A malformed Redis URL must fail validation at startup."""
        from config.settings import settings
        original_broker = settings.event_broker_type
        original_url = settings.redis_url

        try:
            settings.event_broker_type = "redis"
            settings.redis_url = "not-a-url"

            from api import app, lifespan
            with pytest.raises((ValueError, RuntimeError)):
                async with lifespan(app):
                    pass
        finally:
            settings.event_broker_type = original_broker
            settings.redis_url = original_url


# ─── Graceful Shutdown ────────────────────────────────────────────────────────

class TestGracefulShutdown:
    @pytest.mark.asyncio
    async def test_shutdown_does_not_crash_when_core_is_none(self):
        """shutdown_event must handle gideon=None without raising."""
        import api
        original = api.gideon
        api.gideon = None

        from api import app, lifespan
        # Should complete without errors
        async with lifespan(app):
            pass
        api.gideon = original
