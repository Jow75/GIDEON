from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from core.consciousness import SystemConsciousness
import os

app = FastAPI(title="Gideon Core API")

# Initialize consciousness globally
try:
    gideon = SystemConsciousness()
except Exception as e:
    print(f"Warning: Failed to initialize Gideon core on startup: {e}")
    gideon = None

class ChatRequest(BaseModel):
    message: str
    device: str = "Unknown Device"

class MessageResponse(BaseModel):
    role: str
    content: str

class SyncResponse(BaseModel):
    messages: List[MessageResponse]
    world_state: Dict[str, Any]

# Very simple network auth to prevent unauthorized local network/tailnet execution
API_SECRET = os.environ.get("GIDEON_SYNC_SECRET", "default_dev_secret_change_in_production")

def verify_token(x_sync_token: str = Header(None)):
    if x_sync_token != API_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized sync token")
    return True

@app.post("/api/chat")
async def chat(request: ChatRequest, authorized: bool = Depends(verify_token)):
    if not gideon:
        return {"response": "System Consciousness is offline or failed to initialize."}

    try:
        gideon.world_state["Current Device"] = request.device
        response = gideon.process_input(request.message)
        return {"response": response}
    except Exception as e:
        return {"response": f"Error processing request: {str(e)}"}

@app.get("/api/sync", response_model=SyncResponse)
async def sync_state(authorized: bool = Depends(verify_token)):
    if not gideon:
        return SyncResponse(messages=[], world_state={})

    formatted_messages = [
        MessageResponse(role=msg.role, content=msg.content)
        for msg in gideon.history.get_context()
        if msg.role != "system"
    ]

    return SyncResponse(
        messages=formatted_messages,
        world_state=gideon.world_state
    )
