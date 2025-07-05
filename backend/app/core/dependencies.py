# backend/app/core/dependencies.py

from typing import List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import uuid

from .. import models
from .config import settings
from .database import get_db
from .security import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# --- REFACTORED: The Definitive Subdomain/Tenant Dependency ---
def get_tenant_from_subdomain(request: Request, db: Session = Depends(get_db)) -> models.Tenant:
    """
    Determines the current tenant based on the request.

    This function uses a two-pronged approach for maximum flexibility:
    1.  **Header-based (for local dev/testing):** It first checks for a custom
        `X-Tenant-Subdomain` header. This is the primary way to specify a tenant
        during local development or when using API clients like Postman.
    2.  **Host-based (for production):** If the header is not present, it falls
        back to parsing the `Host` header from the incoming request. It assumes a
        format like `subdomain.yourdomain.com`.

    Raises:
        HTTPException(404): If the tenant cannot be determined or is not found.
    
    Returns:
        models.Tenant: The SQLAlchemy Tenant object for the current request.
    """
    subdomain = request.headers.get("x-tenant-subdomain")

    if not subdomain:
        # Fallback to parsing the host header for production environments
        host = request.headers.get("host", "").split(":")[0]
        # Your Render URL is project-mfx.onrender.com. This won't work with subdomains.
        # When you have a custom domain like `mfx-app.com`, `apex.mfx-app.com` will work.
        # For now, the X-Tenant-Subdomain header is the only reliable way.
        parts = host.split('.')
        # Check for a valid subdomain structure (e.g., 'sub.domain.com')
        if len(parts) > 2 and parts[0] != 'www':
            subdomain = parts[0]

    if not subdomain:
        raise HTTPException(
            status_code=400,
            detail="Could not determine tenant. Please provide the subdomain via the 'X-Tenant-Subdomain' header for testing, or use a subdomain in production (e.g., my-org.yourdomain.com)."
        )

    tenant = db.query(models.Tenant).filter(models.Tenant.subdomain == subdomain).first()
    if not tenant:
        raise HTTPException(status_code=404, detail=f"Tenant for subdomain '{subdomain}' not found.")
    
    return tenant


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> models.User:
    """
    Decodes the JWT token, validates it, and fetches the corresponding user.
    """
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
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


class RoleChecker:
    """
    A dependency class to check if the current user has one of the allowed roles.
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: models.User = Depends(get_current_user)):
        """
        Raises:
            HTTPException(403): If the user's role is not in the allowed list.
        """
        if UserRole(current_user.role) not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user does not have sufficient privileges for this action."
            )
        return current_user

# Pre-configured RBAC dependencies for clean endpoint protection
allow_mfi_staff = RoleChecker([UserRole.ADMIN, UserRole.LOAN_OFFICER, UserRole.TELLER, UserRole.AUDITOR])
allow_admin_only = RoleChecker([UserRole.ADMIN])
allow_loan_officer_and_admin = RoleChecker([UserRole.ADMIN, UserRole.LOAN_OFFICER])
allow_teller_and_admin = RoleChecker([UserRole.ADMIN, UserRole.TELLER])
allow_auditor_and_admin = RoleChecker([UserRole.ADMIN, UserRole.AUDITOR])
allow_clients_only = RoleChecker([UserRole.CLIENT])