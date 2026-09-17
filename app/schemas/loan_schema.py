from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


LoanStatus = Literal["active", "returned", "overdue"]


class LoanUserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class LoanDeviceResponse(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str
    brand: Optional[str] = None
    is_available: bool

    model_config = ConfigDict(from_attributes=True)


class LoanCreate(BaseModel):
    user_id: int = Field(gt=0)
    device_id: int = Field(gt=0)
    loan_date: Optional[datetime] = None


class LoanUpdate(BaseModel):
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    status: Optional[LoanStatus] = None


class LoanResponse(BaseModel):
    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: Optional[datetime] = None
    status: LoanStatus

    model_config = ConfigDict(from_attributes=True)


class LoanDetailResponse(LoanResponse):
    user: LoanUserResponse
    device: LoanDeviceResponse
