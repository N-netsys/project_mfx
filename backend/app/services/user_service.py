from sqlalchemy.orm import Session
import uuid
from ..models.user import User
from ..schemas.user import UserCreate
from ..core.security import get_password_hash, verify_password, UserRole
from .. import models, schemas

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(
    db: Session, user_in: UserCreate, role: UserRole, tenant_id: uuid.UUID, client_id: uuid.UUID | None = None
) -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=role.value,
        tenant_id=tenant_id,
        client_id=client_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_team_member(db: Session, member_in: schemas.user.TeamMemberCreate, tenant_id: uuid.UUID) -> User:
    """
    Creates a new user (team member) within a specific tenant.
    This is called by an admin of that tenant.
    """
    # Ensure the new team member role is not a client or investor
    if member_in.role in [UserRole.CLIENT, UserRole.INVESTOR]:
        raise ValueError("Cannot create MFI staff with client or investor role.")

    return create_user(
        db,
        user_in=schemas.user.UserCreate(email=member_in.email, password=member_in.password),
        role=member_in.role,
        tenant_id=tenant_id
    )