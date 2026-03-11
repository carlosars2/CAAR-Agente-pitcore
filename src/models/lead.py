"""Lead-related data models."""

from datetime import datetime

from pydantic import BaseModel, Field


class LeadInfo(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    company_name: str | None = None
    specialty: str | None = None
    employees: int | None = None
    monthly_orders: int | None = None
    main_pain: str | None = None
    interest: str | None = None  # "agent_overlay", "build", "partnership", "monetize"
    recommended_package: str | None = None
    conversation_id: str | None = None
    channel: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConsultationRequest(BaseModel):
    lead: LeadInfo
    preferred_date: str | None = None
    preferred_time: str | None = None
    notes: str | None = None
