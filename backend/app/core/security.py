from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from .config import settings
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    LOAN_OFFICER = "loan_officer"
    TELLER = "teller"  # NEW
    AUDITOR = "auditor"  # NEW
    CLIENT = "client"
    INVESTOR = "investor"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt