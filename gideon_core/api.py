from fastapi import FastAPI
from pydantic import BaseModel
from core.consciousness import SystemConsciousness

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

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not gideon:
        return {"response": "System Consciousness is offline or failed to initialize."}

    try:
        # Update mock state based on incoming request if desired
        gideon.world_state["Current Device"] = request.device
        response = gideon.process_input(request.message)
        return {"response": response}
    except Exception as e:
        return {"response": f"Error processing request: {str(e)}"}
