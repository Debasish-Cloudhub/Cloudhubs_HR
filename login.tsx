from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from models.models import RoleEnum, EmploymentTypeEnum, TimesheetStatusEnum, TimesheetCategoryEnum

# Auth schemas
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    employee_id: Optional[str] = None
    user_id: int
    name: Optional[str] = None

# User schemas
class UserCreate(BaseModel):
    email: str
    password: str
    role: RoleEnum = RoleEnum.employee

class UserOut(BaseModel):
    id: int
    email: str
    role: RoleEnum
    is_active: bool
    class Config:
        from_attributes = True

# Employee schemas
class EmployeeCreate(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    pan: Optional[str] = None
    aadhaar: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc: Optional[str] = None
    pf_number: Optional[str] = None
    uan: Optional[str] = None
    date_of_joining: Optional[date] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    location: Optional[str] = None
    manager_id: Optional[int] = None
    employment_type: EmploymentTypeEnum = EmploymentTypeEnum.permanent
    password: str = "Welcome@123"

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    location: Optional[str] = None
    manager_id: Optional[int] = None

class EmployeeOut(BaseModel):
    id: int
    employee_id: str
    full_name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    pan: Optional[str]
    aadhaar: Optional[str]
    bank_account: Optional[str]
    bank_name: Optional[str]
    ifsc: Optional[str]
    pf_number: Optional[str]
    uan: Optional[str]
    date_of_joining: Optional[date]
    department: Optional[str]
    designation: Optional[str]
    location: Optional[str]
    manager_id: Optional[int]
    employment_type: EmploymentTypeEnum
    is_active: bool
    class Config:
        from_attributes = True

# Timesheet schemas
class TimesheetCreate(BaseModel):
    date: date
    project_name: str
    task_description: str
    hours_worked: float
    category: TimesheetCategoryEnum

class TimesheetUpdate(BaseModel):
    status: TimesheetStatusEnum
    manager_comment: Optional[str] = None
    hr_comment: Optional[str] = None

class TimesheetOut(BaseModel):
    id: int
    employee_id: int
    date: date
    project_name: str
    task_description: str
    hours_worked: float
    category: TimesheetCategoryEnum
    status: TimesheetStatusEnum
    manager_comment: Optional[str]
    hr_comment: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

# Salary component schemas
class SalaryComponentCreate(BaseModel):
    employee_id: int
    basic: float
    hra: float
    allowances: float = 0
    bonus: float = 0
    pf: float = 0
    professional_tax: float = 0
    income_tax: float = 0
    effective_from: date

class SalaryComponentOut(BaseModel):
    id: int
    employee_id: int
    basic: float
    hra: float
    allowances: float
    bonus: float
    pf: float
    professional_tax: float
    income_tax: float
    effective_from: date
    class Config:
        from_attributes = True

# Salary record schemas
class SalaryGenerateRequest(BaseModel):
    employee_id: int
    month: int
    year: int
    worked_days: int
    total_days: int
    lop_days: int = 0

class SalaryRecordOut(BaseModel):
    id: int
    employee_id: int
    month: int
    year: int
    worked_days: int
    total_days: int
    lop_days: int
    basic: float
    hra: float
    allowances: float
    bonus: float
    gross_salary: float
    pf: float
    professional_tax: float
    income_tax: float
    total_deductions: float
    net_salary: float
    created_at: datetime
    class Config:
        from_attributes = True

# Holiday schemas
class HolidayCreate(BaseModel):
    name: str
    date: date
    description: Optional[str] = None
    is_optional: bool = False

class HolidayOut(BaseModel):
    id: int
    name: str
    date: date
    description: Optional[str]
    is_optional: bool
    class Config:
        from_attributes = True

# Document schemas
class DocumentOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: Optional[str]
    filename: str
    created_at: datetime
    class Config:
        from_attributes = True
