from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

BillingCycle = Literal["Monthly", "Yearly"]
Status = Literal["active", "paused"]


class SubscriptionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    cost: float = Field(gt=0)
    billing_cycle: BillingCycle
    renewal_date: date

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name cannot be blank")
        return cleaned

    @field_validator("renewal_date")
    @classmethod
    def not_in_the_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("next renewal date cannot be in the past")
        return value


class SubscriptionStatusUpdate(BaseModel):
    status: Status


class SubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cost: float
    billing_cycle: BillingCycle
    renewal_date: date
    status: Status
    monthly_rate: float
    days_to_renewal: int
    renewing_soon: bool
    overdue: bool
    created_at: datetime
    updated_at: datetime


class MetricsRead(BaseModel):
    monthly_burn_rate: float
    upcoming_renewals_count: int
    active_count: int
    paused_count: int
