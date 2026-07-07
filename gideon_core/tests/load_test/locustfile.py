from locust import HttpUser, task, between
import random
import time
import json
import asyncio
from websockets.sync.client import connect

class GideonUser(HttpUser):
    wait_time = between(1, 3)
    token = None
    
    def on_start(self):
        # Obtain a token to use for subsequent requests
        self._authenticate()

    def _authenticate(self):
        response = self.client.post("/api/auth", json={"device_id": f"locust-{random.randint(1000, 9999)}"})
        if response.status_code == 200:
            self.token = response.json().get("access_token")

    @task(8)
    def chat_request(self):
        if not self.token: return
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.post("/api/chat", json={"message": "Hello Gideon!"}, headers=headers)

    @task(4)
    def sync_request(self):
        if not self.token: return
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.post("/api/sync", json={"device_id": "locust", "last_sync_timestamp": time.time() - 3600}, headers=headers)

    @task(3)
    def websocket_connection(self):
        # Locust doesn't natively support long-lived websockets nicely out of the box in the same HttpUser without 
        # blocking the gevent loop, but we can do a brief connection and disconnection.
        if not self.token: return
        ws_url = self.client.base_url.replace("http", "ws") + f"/api/ws?token={self.token}"
        try:
            with connect(ws_url) as websocket:
                websocket.send(json.dumps({"type": "ping"}))
                websocket.recv(timeout=2)
        except Exception as e:
            # We silently ignore WS timeouts or issues to not skew HTTP stats, or we can log them
            pass

    @task(2)
    def remote_skill_execution(self):
        # We don't have a direct /api/skill endpoint in the core MVP perhaps, but if we route through chat
        # or mock a skill invocation event. For now, simulate via a complex chat request that triggers a skill.
        if not self.token: return
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.post("/api/chat", json={"message": "Execute time skill."}, headers=headers)

    @task(2)
    def research_operations(self):
        if not self.token: return
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.post("/api/chat", json={"message": "Research quantum computing."}, headers=headers)

    @task(1)
    def re_authenticate(self):
        self._authenticate()
