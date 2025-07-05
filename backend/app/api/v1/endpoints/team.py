"""
API endpoints for MFI Admins to manage their team members.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from app.core.dependencies import get_db, allow_admin_only
from services import user_service

router = APIRouter()

@router.post(
    "/members",
    response_model=schemas.user.User,
    dependencies=[Depends(allow_admin_only)],
    status_code=status.HTTP_201_CREATED,
    summary="Add a New Team Member"
)
def add_team_member(
    member_in: schemas.user.TeamMemberCreate,
    current_user: models.User = Depends(allow_admin_only),
    db: Session = Depends(get_db)
):
    """Allows an admin to invite/create a new user within their organization."""
    return user_service.create_team_member(db, member_in=member_in, tenant_id=current_user.tenant_id)

@router.get(
    "/members",
    response_model=List[schemas.user.User],
    dependencies=[Depends(allow_admin_only)],
    summary="List All Team Members"
)
def list_team_members(
    current_user: models.User = Depends(allow_admin_only),
    db: Session = Depends(get_db)
):
    """Returns a list of all users belonging to the admin's tenant."""
    return db.query(models.User).filter(models.User.tenant_id == current_user.tenant_id).all()