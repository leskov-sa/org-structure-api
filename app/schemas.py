from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List

class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: Optional[int] = None

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[int] = None

class DepartmentOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class EmployeeCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    position: str = Field(..., min_length=1, max_length=200)
    hired_at: Optional[date] = None

class EmployeeOut(BaseModel):
    id: int
    department_id: int
    full_name: str
    position: str
    hired_at: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True
