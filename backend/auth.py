"""
SilverSentinel Authentication Module
JWT-based authentication for API endpoints
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from dotenv import load_dotenv
load_dotenv()

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
API_KEY_HEADER = "X-API-Key"

# Optional: API keys for service-to-service auth
VALID_API_KEYS = set(filter(None, os.getenv("API_KEYS", "").split(",")))

# Security scheme
security = HTTPBearer(auto_error=False)


@dataclass
class TokenData:
    """JWT token payload data"""
    user_id: str
    email: str
    name: str
    exp: datetime
    iat: datetime


@dataclass 
class User:
    """User model for authentication"""
    id: str
    email: str
    name: str
    password_hash: str
    salt: str
    created_at: datetime
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }


# In-memory user store (for hackathon demo)
# In production, use database
_users: Dict[str, User] = {}


def hash_password(password: str, salt: str) -> str:
    """Hash password with salt using SHA-256"""
    return hashlib.sha256((password + salt).encode()).hexdigest()


def generate_salt() -> str:
    """Generate random salt"""
    return secrets.token_hex(16)


def create_user(email: str, password: str, name: str) -> Optional[User]:
    """Create a new user"""
    if email in _users:
        return None  # User exists
    
    salt = generate_salt()
    user = User(
        id=secrets.token_hex(8),
        email=email,
        name=name,
        password_hash=hash_password(password, salt),
        salt=salt,
        created_at=datetime.utcnow()
    )
    _users[email] = user
    return user


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = _users.get(email)
    if not user:
        return None
    
    if hash_password(password, user.salt) != user.password_hash:
        return None
    
    return user


def create_access_token(user: User) -> str:
    """Create JWT access token"""
    now = datetime.utcnow()
    payload = {
        "sub": user.id,
        "email": user.email,
        "name": user.name,
        "iat": now,
        "exp": now + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return TokenData(
            user_id=payload["sub"],
            email=payload["email"],
            name=payload["name"],
            exp=datetime.fromtimestamp(payload["exp"]),
            iat=datetime.fromtimestamp(payload["iat"])
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def validate_api_key(api_key: str) -> bool:
    """Validate API key for service-to-service auth"""
    if not VALID_API_KEYS:
        return True  # No API keys configured, allow all
    return api_key in VALID_API_KEYS


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[TokenData]:
    """
    Dependency to get current authenticated user from JWT token.
    Returns None if no valid token (allows optional auth).
    """
    if not credentials:
        return None
    
    token_data = decode_token(credentials.credentials)
    return token_data


async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> TokenData:
    """
    Dependency that requires valid authentication.
    Raises 401 if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token_data = decode_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return token_data


async def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[TokenData]:
    """
    Dependency for optional authentication.
    Returns user data if authenticated, None otherwise.
    """
    if not credentials:
        return None
    
    return decode_token(credentials.credentials)


# Create a demo user for development
def init_demo_user():
    """Initialize a demo user for development/testing"""
    demo_email = os.getenv("DEMO_USER_EMAIL", "demo@silversentinel.ai")
    demo_password = os.getenv("DEMO_USER_PASSWORD", "demo123")
    demo_name = os.getenv("DEMO_USER_NAME", "Demo User")
    
    if demo_email not in _users:
        create_user(demo_email, demo_password, demo_name)
        print(f"  Demo user created: {demo_email}")


# Initialize demo user on module load
init_demo_user()
