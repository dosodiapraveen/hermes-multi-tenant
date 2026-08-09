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

class UserModelOverride(BaseModel):
    """Override the model for a specific user."""
    primary_model: Optional[str] = None
    backup_model: Optional[str] = None

class UserSkillCreate(BaseModel):
    """Add or update a skill file for a user."""
    skill_name: str = Field(..., min_length=1, max_length=200, description="Skill filename (e.g. 'custom-instructions.md')")
    content: str = Field(..., min_length=1, description="Full markdown content of the skill")

class GlobalSkillTemplate(BaseModel):
    """Add or update a skill template pushed to all users."""
    skill_name: str = Field(..., min_length=1, max_length=200, description="Skill filename (e.g. 'global-instructions.md')")
    content: str = Field(..., min_length=1, description="Full markdown content of the skill")
    user_ids: Optional[list[str]] = Field(None, description="Optional specific user IDs to target (default: all)")
