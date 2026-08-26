from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    full_name: str
    role: str
    organization_id: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    verification_document_type: str = "ROLE_VERIFICATION"
    verification_details: dict = Field(default_factory=dict)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    full_name: str
    role: str
    organization_id: Optional[int] = None
    is_active: bool
    is_approved: bool


class VerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    document_type: str
    verification_status: str
    verification_details: dict | None = None
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class BatchCreate(BaseModel):
    batch_id: str
    herb_name: str
    scientific_name: str
    quantity: float
    unit: str
    collection_date: datetime
    collection_location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    collector: str
    initial_holder: str
    source_type: Optional[str] = None
    notes: Optional[str] = None


class BatchCreateRequest(BaseModel):
    herb_name: str = Field(min_length=2, max_length=255)
    scientific_name: str = Field(min_length=2, max_length=255)
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=50)
    collection_date: datetime
    collection_location: str = Field(min_length=2, max_length=255)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    source_type: Optional[str] = None
    notes: Optional[str] = None


class BatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    batch_id: str
    herb_name: str
    scientific_name: str
    quantity: float
    unit: str
    collection_date: datetime
    collection_location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    collector_id: Optional[int] = None
    initial_holder_id: Optional[int] = None
    current_holder_id: Optional[int] = None
    status: str
    recall_status: str


class OrganizationCreate(BaseModel):
    name: str
    type: str
    location: Optional[str] = None


class SuspiciousEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: Optional[str]
    event_type: str
    severity: str
    description: str
    status: str
    timestamp: datetime
