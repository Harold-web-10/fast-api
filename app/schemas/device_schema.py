from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    name: str = Field(min_length=3)
    serial_number: str = Field(min_length=3)
    device_type: str = Field(min_length=1)
    brand: Optional[str] = Field(default=None, max_length=100)


class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3)
    serial_number: Optional[str] = Field(default=None, min_length=3)
    device_type: Optional[str] = Field(default=None, min_length=1)
    brand: Optional[str] = Field(default=None, max_length=100)
    is_available: Optional[bool] = None


class DeviceResponse(DeviceCreate):
    id: int
    is_available: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
