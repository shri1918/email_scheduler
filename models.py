from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EmailJobStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DELETED = "deleted"


class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    name: str
    google_id: str
    access_token: str
    refresh_token: Optional[str] = None 
    token_expiry: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EmailJob(BaseModel):
    id: Optional[str] = None
    user_id: str
    recipient: EmailStr
    subject: str
    body: str
    attachments: List[str] = []
    every_n_days: int = Field(gt=0, description="Send email every N days")
    last_sent: Optional[datetime] = None
    next_send: Optional[datetime] = None
    status: EmailJobStatus = EmailJobStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EmailJobCreate(BaseModel):
    recipient: EmailStr
    subject: str
    body: str
    attachments: List[str] = []
    every_n_days: int = Field(gt=0, description="Send email every N days")


class EmailJobUpdate(BaseModel):
    recipient: Optional[EmailStr] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    attachments: Optional[List[str]] = None
    every_n_days: Optional[int] = Field(None, gt=0)
    status: Optional[EmailJobStatus] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


class GoogleAuthResponse(BaseModel):
    code: str
    state: Optional[str] = None


class EmailSendResult(BaseModel):
    job_id: str
    recipient: EmailStr
    subject: str
    sent_at: datetime
    success: bool
    error_message: Optional[str] = None 