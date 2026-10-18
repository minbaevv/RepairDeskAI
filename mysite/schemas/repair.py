from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

RepairStatus = Literal["new", "in_progress", "done", "cancelled"]


class RepairCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    client_name: str = Field(min_length=1, max_length=100)
    device: str = Field(min_length=1, max_length=150)
    problem: str = Field(min_length=1, max_length=1500)


class RepairUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    problem: str | None = Field(default=None, min_length=1, max_length=1500)
    status: RepairStatus | None = None

    @model_validator(mode="after")
    def validate_changes(self):
        if self.problem is None and self.status is None:
            raise ValueError("Укажите problem или status")
        return self


class RepairRead(RepairCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: RepairStatus
    created_at: datetime


class RepairList(BaseModel):
    count: int
    items: list[RepairRead]
