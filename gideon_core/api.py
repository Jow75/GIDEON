from fastapi import FastAPI, Depends, HTTPException, Header, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import logging
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from core.consciousness import SystemConsciousness
from core.events.models import Event
from core.auth import AuthManager, UserSession, UserRole, DeviceIdentity, AuthError
from config.settings import settings
import os
from core.observability import setup_observability

# Initialize consciousness globally
gideon = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global gideon
    
    # 1. Configuration Validation
    if not settings.disable_auth_for_dev:
        if not settings.jwt_secret or settings.jwt_secret == "default_jwt_secret_change_in_production":
            if settings.environment == "production":
                raise RuntimeError("CRITICAL: Missing secure JWT secret in production.")
                
    if settings.event_broker_type == "redis":
        if not settings.redis_url or not settings.redis_url.startswith("redis://"):
            raise ValueError("CRITICAL: Invalid or missing REDIS_URL")
        # Quick sync test for redis URL
        # We will do a full test in liveness if needed, but fail fast if clearly broken
    
    # 2. Boot Core
    try:
        gideon = SystemConsciousness()
        if hasattr(gideon, "initialize"):
            await gideon.initialize()
    except Exception as e:
        print(f"CRITICAL: Failed to initialize Gideon core on startup: {e}")
        # Fail immediately per WP2 guidelines
        raise RuntimeError("Gideon Core Initialization Failed") from e

    yield

    # Shutdown
    if gideon:
        if hasattr(gideon, "stop"):
            await gideon.stop()
        else:
            await gideon.event_bus.stop()
        # Ensure any long-running tasks or connections are flushed
        import logging
        logging.info("Gideon Core shutdown cleanly.")

app = FastAPI(title="Gideon Core API", lifespan=lifespan)

if settings.event_broker_type == "redis" and settings.redis_url:
    limiter = Limiter(key_func=get_remote_address, storage_uri=settings.redis_url)
else:
    limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

audit_logger = logging.getLogger("audit")

# Setup Tracing, Metrics, and JSON Logging
setup_observability(app)

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))



@app.get("/health")
async def health():
    """Overall system health."""
    return {"status": "ok", "version": "1.0.0"}

@app.get("/liveness")
async def liveness():
    """Kubernetes liveness probe. Indicates if container is running."""
    return {"status": "alive"}

@app.get("/readiness")
async def readiness():
    """Kubernetes readiness probe. Indicates if app is ready to receive traffic."""
    if not gideon:
        raise HTTPException(status_code=503, detail="Core not initialized")
        
    # Check DB/Redis
    if settings.event_broker_type == "redis":
        try:
            # We assume broker has a ping or is connected if no exception
            if not getattr(gideon.event_bus._broker, "redis", None):
                raise HTTPException(status_code=503, detail="Redis disconnected")
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Redis error: {e}")
            
    return {"status": "ready"}

class ChatRequest(BaseModel):
    message: str
    device: str = "Unknown Device"

class MessageResponse(BaseModel):
    role: str
    content: str

class SyncResponse(BaseModel):
    messages: List[MessageResponse]
    world_state: Dict[str, Any]

class TokenRequest(BaseModel):
    subject: str
    role: str = "USER"
    device_id: str = "unknown"
    device_type: str = "unknown"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def verify_jwt(authorization: str = Header(None)) -> UserSession:
    if settings.disable_auth_for_dev:
        return UserSession(subject="dev_user", role=UserRole.ADMIN)
        
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        
    token = authorization.split(" ")[1]
    try:
        session = AuthManager.verify_token(token)
        return session
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/api/auth/token", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login_for_access_token(request: Request, token_request: TokenRequest):
    try:
        role = UserRole(token_request.role)
    except ValueError:
        audit_logger.warning(f"Auth failed: invalid role {token_request.role} for {token_request.subject}")
        raise HTTPException(status_code=400, detail="Invalid role specified")
        
    device = DeviceIdentity(device_id=token_request.device_id, device_type=token_request.device_type)
    token = AuthManager.create_access_token(subject=token_request.subject, role=role, device=device)
    
    audit_logger.info(f"Auth success for {token_request.subject} via {token_request.device_id}")
    return TokenResponse(access_token=token)

@app.post("/api/chat")
@limiter.limit("60/minute")
async def chat(request: Request, chat_req: ChatRequest, session: UserSession = Depends(verify_jwt)):
    if not gideon:
        return {"response": "System Consciousness is offline or failed to initialize."}

    audit_logger.info(f"Chat request from {session.subject} via {chat_req.device}")
    try:
        await gideon.sync_manager.update_state("Current Device", chat_req.device)
        response = await gideon.process_input(chat_req.message)
        return {"response": response}
    except Exception as e:
        return {"response": f"Error processing request: {str(e)}"}

@app.get("/api/sync", response_model=SyncResponse)
async def sync_state(session: UserSession = Depends(verify_jwt)):
    if not gideon:
        return SyncResponse(messages=[], world_state={})

    history_messages = await gideon.history.get_context(gideon.session_id)
    formatted_messages = [
        MessageResponse(role=msg.role, content=msg.content)
        for msg in history_messages
        if msg.role != "system"
    ]

    return SyncResponse(
        messages=formatted_messages,
        world_state=gideon.world_state
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    await websocket.accept()
    
    if not settings.disable_auth_for_dev:
        if not token:
            await websocket.close(code=1008, reason="Missing authentication token")
            return
        try:
            session = AuthManager.verify_token(token)
        except AuthError:
            await websocket.close(code=1008, reason="Invalid authentication token")
            return
            
    if not gideon:
        await websocket.close(code=1011)
        return

    # Create a unique queue for this connection
    queue = asyncio.Queue()

    async def event_handler(event: Event):
        await queue.put(event)

    # Subscribe to all events ("*") to stream everything to the frontend
    gideon.event_bus.subscribe("*", event_handler)
    
    # Request an initial snapshot of the world state for this client
    # The client will receive a state_snapshot_response
    await gideon.sync_manager.request_snapshot()

    try:
        while True:
            event = await queue.get()
            payload = {
                "type": event.type,
                "source": event.source,
                "payload": event.payload,
                "timestamp": event.timestamp.isoformat()
            }
            await websocket.send_json(payload)
            queue.task_done()
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        gideon.event_bus.unsubscribe("*", event_handler)
