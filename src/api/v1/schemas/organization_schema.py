from pydantic import BaseModel, ConfigDict
from typing import Optional
from src.database.models.enums import OrgType

class OrganizationBase(BaseModel):
    name: str
    type: OrgType
    address: Optional[str] = None
    is_certified: Optional[bool] = False

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[OrgType] = None
    address: Optional[str] = None
    is_certified: Optional[bool] = None

class OrganizationResponse(OrganizationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class OrganizationListResponse(BaseModel):
    total: int
    organizations: list[OrganizationResponse]
