import unittest
from fastapi.testclient import TestClient
from api import app, gideon

client = TestClient(app)

class TestSyncAPI(unittest.TestCase):
    def test_sync_endpoint_unauthorized(self):
        response = client.get("/api/sync")
        self.assertEqual(response.status_code, 401)

    def test_sync_endpoint_authorized(self):
        if gideon:
            gideon.history.clear()
            gideon.history.add_user_message("Hello from test")
            gideon.world_state["Active Mission"] = "Test Mission"

        response = client.get("/api/sync", headers={"x-sync-token": "default_dev_secret_change_in_production"})
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("messages", data)
        self.assertIn("world_state", data)

if __name__ == '__main__':
    unittest.main()
