from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import uuid

from .config import settings
from .database import get_db
from .security import UserRole
from ..models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if UserRole(current_user.role) not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user does not have sufficient privileges for this action."
            )
        return current_user

allow_mfi_staff = RoleChecker([UserRole.ADMIN, UserRole.LOAN_OFFICER, UserRole.TELLER, UserRole.AUDITOR])
allow_admin_only = RoleChecker([UserRole.ADMIN])
allow_loan_officer_and_admin = RoleChecker([UserRole.ADMIN, UserRole.LOAN_OFFICER])
allow_teller_and_admin = RoleChecker([UserRole.ADMIN, UserRole.TELLER]) # NEW
allow_auditor_and_admin = RoleChecker([UserRole.ADMIN, UserRole.AUDITOR]) # NEW
allow_clients_only = RoleChecker([UserRole.CLIENT])
allow_investors_only = RoleChecker([UserRole.INVESTOR])