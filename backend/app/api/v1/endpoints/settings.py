"""
API endpoints for managing tenant-specific settings.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..core.dependencies import get_db, allow_admin_only

router = APIRouter()

@router.get("/", response_model=schemas.tenant.TenantSettings)
def get_tenant_settings(
    current_user: models.User = Depends(allow_admin_only),
    db: Session = Depends(get_db)
):
    settings = db.query(models.tenant.TenantSettings).filter(
        models.tenant.TenantSettings.tenant_id == current_user.tenant_id
    ).first()
    return settings

@router.put("/", response_model=schemas.tenant.TenantSettings, dependencies=[Depends(allow_admin_only)])
def update_tenant_settings(
    settings_in: schemas.tenant.TenantSettingsUpdate,
    current_user: models.User = Depends(allow_admin_only),
    db: Session = Depends(get_db)
):
    """Allows an admin to update their organization's settings."""
    db_settings = db.query(models.tenant.TenantSettings).filter(
        models.tenant.TenantSettings.tenant_id == current_user.tenant_id
    ).first()

    if not db_settings:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Settings not found.")
    
    update_data = settings_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_settings, key, value)
        
    db.commit()
    db.refresh(db_settings)
    return db_settings