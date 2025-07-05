# backend/app/schemas/tenant.py

import uuid
from pydantic import BaseModel, constr, validator

class OrganizationRegistration(BaseModel):
    organization_name: str
    subdomain: constr(lower=True, strip_whitespace=True, min_length=3)
    admin_email: str
    admin_password: constr(min_length=8)

    @validator('subdomain')
    def validate_subdomain(cls, v):
        if not v.isalnum():
            raise ValueError('Subdomain must be alphanumeric')
        # You might want to add a list of reserved subdomains like 'www', 'api', 'app'
        if v in ['www', 'api', 'app', 'admin']:
             raise ValueError(f"Subdomain '{v}' is reserved.")
        return v


class TenantSettingsUpdate(BaseModel):
    currency: str | None = None
    configurations: dict | None = None

class TenantSettings(TenantSettingsUpdate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    class Config:
        from_attributes = True