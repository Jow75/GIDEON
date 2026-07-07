import unittest
from fastapi.testclient import TestClient
from api import app, gideon
from core.auth import AuthManager, UserRole, DeviceIdentity

client = TestClient(app)

class TestSyncAPI(unittest.TestCase):
    def test_sync_endpoint_unauthorized(self):
        response = client.get("/api/sync")
        self.assertEqual(response.status_code, 401)

    def test_sync_endpoint_authorized(self):
        if gideon:
            gideon.history.clear()
            gideon.history.add_message(gideon.session_id, "user", "Hello from test")
            gideon.world_state["Active Mission"] = "Test Mission"
            
        device = DeviceIdentity(device_id="test_sync", device_type="test")
        token = AuthManager.create_access_token("user1", UserRole.USER, device)
    
        response = client.get("/api/sync", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("messages", data)
        self.assertIn("world_state", data)

if __name__ == '__main__':
    unittest.main()
