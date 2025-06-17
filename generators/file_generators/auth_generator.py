"""
Authentication Generator
Generates authentication and security files
"""

from ..base_generator import BaseGenerator
from ..config import AuthType


class AuthGenerator(BaseGenerator):
    """Generates authentication files"""

    def should_generate(self) -> bool:
        """Only generate if authentication is enabled"""
        return self.config.auth_type != AuthType.NONE

    def generate(self):
        """Generate authentication files"""
        # Generate security.py
        security_content = self._get_security_template()
        self.write_file(f"{self.config.path}/app/core/security.py", security_content)

        # Generate auth models if using JWT or OAuth2
        if self.config.auth_type in [AuthType.JWT, AuthType.OAUTH2]:
            auth_models_content = self._get_auth_models_template()
            self.write_file(
                f"{self.config.path}/app/models/auth.py", auth_models_content
            )

            auth_schemas_content = self._get_auth_schemas_template()
            self.write_file(
                f"{self.config.path}/app/schemas/auth.py", auth_schemas_content
            )

    def _get_security_template(self) -> str:
        """Get security template based on auth type"""
        if self.config.auth_type == AuthType.JWT:
            return self._get_jwt_template()
        elif self.config.auth_type == AuthType.OAUTH2:
            return self._get_oauth2_template()
        elif self.config.auth_type == AuthType.API_KEY:
            return self._get_api_key_template()
        return ""

    def _get_jwt_template(self) -> str:
        """Get JWT authentication template"""
        template = '''"""
JWT Authentication Security
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.models.auth import User
from app.schemas.auth import TokenData

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update(dict(exp=expire))
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return TokenData(email=email)
    except JWTError:
        return None


{async_user_functions}


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


{async_current_user}
'''

        if self.config.is_async:
            async_user_functions = '''
async def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def create_user(db: Session, email: str, password: str) -> User:
    """Create new user"""
    hashed_password = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
'''

            async_current_user = '''
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={{"WWW-Authenticate": "Bearer"}},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    user = await get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    
    return user
'''
        else:
            sync_user_functions = '''
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password: str) -> User:
    """Create new user"""
    hashed_password = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
'''

            sync_current_user = '''
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={{"WWW-Authenticate": "Bearer"}},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    
    return user
'''
        template_vars = {
            "async_user_functions": (
                async_user_functions if self.config.is_async else ""
            ),
            "sync_user_functions": (
                sync_user_functions if not self.config.is_async else ""
            ),
            "async_current_user": async_current_user if self.config.is_async else "",
            "sync_current_user": sync_current_user if not self.config.is_async else "",
        }

        return self.format_template(template.format(**template_vars))

    def _get_oauth2_template(self) -> str:
        """Get OAuth2 authentication template"""
        template = '''"""
OAuth2 Authentication Security
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{{settings.API_PREFIX}}/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from OAuth2 token"""
    # Implement OAuth2 token validation logic here
    # This is a placeholder implementation
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={{"WWW-Authenticate": "Bearer"}},
    )
    
    # Add your OAuth2 provider integration here
    # For example: Google, GitHub, Auth0, etc.
    
    raise credentials_exception
'''

        return self.format_template(template)

    def _get_api_key_template(self) -> str:
        """Get API Key authentication template"""
        template = '''"""
API Key Authentication Security
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key: str = Depends(api_key_header)):
    """Validate API key"""
    # In production, store API keys in database or secure storage
    valid_api_keys = ["your-api-key-here"]  # Replace with actual API keys
    
    if api_key not in valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    
    return api_key
'''

        return self.format_template(template)

    def _get_auth_models_template(self) -> str:
        """Get authentication models template"""
        template = '''"""
Authentication Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import BaseModel


class User(BaseModel):
    """User model"""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {{self.email}}>"
'''

        return self.format_template(template)

    def _get_auth_schemas_template(self) -> str:
        """Get authentication schemas template"""
        template = '''"""
Authentication Schemas
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    email: Optional[str] = None


class UserBase(BaseModel):
    """User base schema"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserUpdate(UserBase):
    """User update schema"""
    password: Optional[str] = None


class User(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    is_superuser: bool
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str
'''

        return self.format_template(template)
