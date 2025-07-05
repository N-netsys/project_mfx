# backend/app/schemas/tenant.py

import uuid
from pydantic import BaseModel, constr, validator

class OrganizationRegistration(BaseModel):
    organization_name: str
    subdomain: str
    admin_email: str
    admin_password: constr(min_length=8)

    @validator('subdomain', pre=True)
    def clean_and_validate_subdomain(cls, v):
        """
        A custom validator that performs all necessary cleaning and validation for the subdomain.
        `pre=True` means this runs before any other validation on the field.
        """
        if not isinstance(v, str):
            raise ValueError('Subdomain must be a string')
        
        # 1. Strip whitespace and convert to lowercase
        cleaned_subdomain = v.strip().lower()
        
        # 2. Perform length and content validation
        if len(cleaned_subdomain) < 3:
            raise ValueError('Subdomain must be at least 3 characters long')
            
        if not cleaned_subdomain.isalnum():
            raise ValueError('Subdomain must be alphanumeric')
        
        # 3. Check for reserved names
        if cleaned_subdomain in ['www', 'api', 'app', 'admin', 'mfx', 'test']:
             raise ValueError(f"Subdomain '{cleaned_subdomain}' is reserved.")
             
        return cleaned_subdomain


class TenantSettingsUpdate(BaseModel):
    currency: str | None = None
    configurations: dict | None = None


class TenantSettings(TenantSettingsUpdate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    class Config:
        from_attributes = True