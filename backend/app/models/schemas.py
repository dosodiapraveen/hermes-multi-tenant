from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InviteLinkCreate(BaseModel):
    label: str = Field(..., min_length=1, max_length=200)
    agent_name: str = Field(default="My Assistant", max_length=100)
    plan: str = Field(default="pro", pattern="^(trial|basic|pro|business|vip)$")
    trial_days: Optional[int] = Field(default=7, ge=1, le=365)
    is_vip: bool = False

class InviteLinkRedeem(BaseModel):
    code: str
    phone_number: str

class ModelConfigUpdate(BaseModel):
    primary_model: Optional[str] = None
    backup_model: Optional[str] = None

class UserOverride(BaseModel):
    user_id: str
    primary_model: Optional[str] = None
    backup_model: Optional[str] = None
