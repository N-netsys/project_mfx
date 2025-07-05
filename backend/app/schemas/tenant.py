import uuid
from pydantic import BaseModel, constr

# --- NEW: Schema for the registration endpoint ---
class OrganizationRegistration(BaseModel):
    organization_name: str
    admin_email: str
    admin_password: constr(min_length=8)

class TenantSettingsUpdate(BaseModel):
    currency: str | None = None
    configurations: dict | None = None

class TenantSettings(TenantSettingsUpdate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    class Config:
        from_attributes = True