import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, Header
from pydantic import BaseModel

try:
    from jose import JWTError, jwt
except ImportError:  # pragma: no cover - fallback for local/dev environments
    JWTError = Exception
    jwt = None

try:
    from passlib.context import CryptContext
except ImportError:  # pragma: no cover - fallback for local/dev environments
    CryptContext = None

try:
    from sqlalchemy import create_engine, Column, Integer, String, DateTime
    from sqlalchemy.orm import declarative_base, sessionmaker
except ImportError:  # pragma: no cover - fallback for local/dev environments
    create_engine = None
    Column = Integer = String = DateTime = None
    declarative_base = sessionmaker = None

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if CryptContext is not None:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    class _FallbackHash:
        def hash(self, password: str) -> str:
            return f"fake_hash:{password}"

        def verify(self, password: str, password_hash: str) -> bool:
            return password_hash == f"fake_hash:{password}"

    pwd_context = _FallbackHash()


class UserCreate(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInDB(BaseModel):
    email: str
    password_hash: str


if create_engine is not None and declarative_base is not None and sessionmaker is not None:
    Base = declarative_base()

    class AuthUser(Base):
        __tablename__ = "auth_users"
        id = Column(Integer, primary_key=True, index=True)
        email = Column(String(255), unique=True, nullable=False, index=True)
        password_hash = Column(String(255), nullable=False)
        created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)

    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/appdb")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
else:
    Base = None
    AuthUser = None
    SessionLocal = None


class AuthUserStore:
    def __init__(self):
        self.users: dict[str, UserInDB] = {}
        self._db_session = None
        if SessionLocal is not None:
            self._db_session = SessionLocal()

    def _get_session(self):
        if self._db_session is None:
            return None
        return self._db_session

    def create_user(self, email: str, password: str) -> UserInDB:
        if email in self.users:
            raise HTTPException(status_code=400, detail="Email already registered")
        password_hash = pwd_context.hash(password)
        if SessionLocal is not None and AuthUser is not None:
            session = self._get_session()
            existing = session.query(AuthUser).filter(AuthUser.email == email).first() if session is not None else None
            if existing is not None:
                raise HTTPException(status_code=400, detail="Email already registered")
            user_row = AuthUser(email=email, password_hash=password_hash)
            session.add(user_row)
            session.commit()
        user = UserInDB(email=email, password_hash=password_hash)
        self.users[email] = user
        return user

    def authenticate(self, email: str, password: str) -> Optional[UserInDB]:
        if SessionLocal is not None and AuthUser is not None:
            session = self._get_session()
            if session is not None:
                user_row = session.query(AuthUser).filter(AuthUser.email == email).first()
                if user_row is not None and pwd_context.verify(password, user_row.password_hash):
                    return UserInDB(email=user_row.email, password_hash=user_row.password_hash)
        user = self.users.get(email)
        if not user:
            return None
        if not pwd_context.verify(password, user.password_hash):
            return None
        return user


AUTH_STORE = AuthUserStore()


def create_access_token(email: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    if jwt is None:
        return f"token:{email}:{int(expires.timestamp())}"
    return jwt.encode({"sub": email, "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str:
    if jwt is None:
        if token.startswith("token:"):
            parts = token.split(":")
            if len(parts) >= 3:
                return parts[1]
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return email


def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    token = authorization.split(" ", 1)[1].strip()
    return decode_access_token(token)
