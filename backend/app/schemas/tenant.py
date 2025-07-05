# backend/app/schemas/tenant.py

import uuid
from pydantic import BaseModel, constr, validator, Field
from typing_extensions import Annotated

class OrganizationRegistration(BaseModel):
    organization_name: str
    
    # Pydantic V2 uses Annotated types for string constraints
    subdomain: Annotated[
        str,
        Field(min_length=3),
        # Pydantic V2 uses StringConstraints for stripping whitespace
        # However, we will handle both stripping and lowercasing in the validator below
        # for a cleaner implementation.
    ]

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

        # 1. Strip whitespace and convert to lowercase (replaces old constr arguments)
        cleaned_subdomain = v.strip().lower()

        # 2. Perform validation checks
        if not cleaned_subdomain.isalnum():
            raise ValueError('Subdomain must be alphanumeric')

        if cleaned_subdomain in ['www', 'api', 'app', 'admin', 'mfx']:
            raise ValueError(f"Subdomain '{cleaned_subdomain}' is reserved.")

        return cleaned_subdomain

    subdomain: Annotated[
        str,
        Field(min_length=3),
        # Pydantic V2 uses StringConstraints for stripping whitespace
        # However, we will handle both stripping and lowercasing in the validator below
        # for a cleaner implementation.
    ]
    
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
        
        # 1. Strip whitespace and convert to lowercase (replaces old constr arguments)
        cleaned_subdomain = v.strip().lower()

        # 2. Perform validation checks
        if not cleaned_subdomain.isalnum():
            raise ValueError('Subdomain must be alphanumeric')
        
        if cleaned_subdomain in ['www', 'api', 'app', 'admin', 'mfx']:
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