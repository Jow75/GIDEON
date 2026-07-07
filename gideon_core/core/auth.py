from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from config.settings import settings

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    DEVICE = "DEVICE"
    READ_ONLY = "READ_ONLY"

class DeviceIdentity(BaseModel):
    device_id: str
    device_type: str
    ip_address: Optional[str] = None

class UserSession(BaseModel):
    subject: str
    role: UserRole
    device: Optional[DeviceIdentity] = None
    exp: Optional[int] = None

class AuthError(Exception):
    pass

class TokenExpiredError(AuthError):
    pass

class InvalidTokenError(AuthError):
    pass

class AuthManager:
    """Handles JWT generation and validation."""
    
    @staticmethod
    def create_access_token(subject: str, role: UserRole, device: Optional[DeviceIdentity] = None) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        
        payload = {
            "sub": subject,
            "role": role.value,
            "exp": expire
        }
        if device:
            payload["device"] = device.model_dump()
            
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        
    @staticmethod
    def create_refresh_token(subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
        payload = {
            "sub": subject,
            "type": "refresh",
            "exp": expire
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    @staticmethod
    def verify_token(token: str) -> UserSession:
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            
            if payload.get("type") == "refresh":
                raise InvalidTokenError("Cannot use refresh token as access token.")
                
            device_data = payload.get("device")
            device = DeviceIdentity(**device_data) if device_data else None
            
            subject = payload.get("sub")
            if not subject:
                raise InvalidTokenError("Token missing required 'sub' claim.")
            
            return UserSession(
                subject=subject,
                role=UserRole(payload.get("role")),
                device=device,
                exp=payload.get("exp")
            )
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired.")
        except jwt.PyJWTError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
