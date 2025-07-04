from sqlalchemy.orm import Session
from ..schemas.user import UserCreate  # Import UserCreate directly
from ..models.user import User
from ..core.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> User | None: # Use 'User', not 'models.User'
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(  # Use 'User'
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        tenant_id=user.tenant_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> User | None: # Use 'User'
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user