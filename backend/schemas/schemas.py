from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from models.models import RoleEnum, EmploymentTypeEnum, TimesheetStatusEnum

class LoginRequest(BaseModel):
    email: EmailStr; password: str

class TokenResponse(BaseModel):
    access_token: str; token_type: str = "bearer"; role: str; user_id: int

class EmployeeCreate(BaseModel):
    email: EmailStr; password: str; first_name: str; last_name: str
    phone: Optional[str] = None; designation: Optional[str] = None
    department: Optional[str] = None
    employment_type: EmploymentTypeEnum = EmploymentTypeEnum.permanent
    date_of_joining: Optional[date] = None; date_of_birth: Optional[date] = None
    address: Optional[str] = None; bank_account: Optional[str] = None
    bank_name: Optional[str] = None; ifsc_code: Optional[str] = None
    pf_number: Optional[str] = None; uan_number: Optional[str] = None

class EmployeeOut(BaseModel):
    id: int; employee_id: str; first_name: str; last_name: str; email: str
    phone: Optional[str]; designation: Optional[str]; department: Optional[str]
    employment_type: EmploymentTypeEnum; date_of_joining: Optional[date]
    date_of_birth: Optional[date]; address: Optional[str]; bank_account: Optional[str]
    bank_name: Optional[str]; ifsc_code: Optional[str]; pf_number: Optional[str]
    uan_number: Optional[str]; is_active: bool; created_at: datetime
    class Config: from_attributes = True

class TimesheetCreate(BaseModel):
    date: date; hours_worked: float = 8.0
    task_description: Optional[str] = None; project: Optional[str] = None

class TimesheetApprove(BaseModel):
    status: TimesheetStatusEnum; rejection_reason: Optional[str] = None

class TimesheetOut(BaseModel):
    id: int; date: date; hours_worked: float; task_description: Optional[str]
    project: Optional[str]; status: TimesheetStatusEnum
    rejection_reason: Optional[str]; created_at: datetime
    class Config: from_attributes = True

class SalaryComponentCreate(BaseModel):
    employee_id: int; basic: float = 0; hra: float = 0; allowances: float = 0
    bonus: float = 0; pf_deduction: float = 0; professional_tax: float = 0
    income_tax: float = 0; effective_from: Optional[date] = None

class SalaryComponentOut(BaseModel):
    id: int; employee_id: int; basic: float; hra: float; allowances: float
    bonus: float; pf_deduction: float; professional_tax: float; income_tax: float
    effective_from: Optional[date]
    class Config: from_attributes = True

class SalaryGenerateRequest(BaseModel):
    employee_id: int; month: int; year: int

class SalaryRecordOut(BaseModel):
    id: int; employee_id: int; month: int; year: int; basic: float; hra: float
    allowances: float; bonus: float; gross_salary: float; pf_deduction: float
    professional_tax: float; income_tax: float; total_deductions: float
    net_salary: float; generated_at: datetime
    class Config: from_attributes = True

class HolidayCreate(BaseModel):
    name: str; date: date; description: Optional[str] = None; is_optional: bool = False

class HolidayOut(BaseModel):
    id: int; name: str; date: date; description: Optional[str]; is_optional: bool
    class Config: from_attributes = True

class DocumentOut(BaseModel):
    id: int; title: str; description: Optional[str]; file_name: str
    is_public: bool; created_at: datetime
    class Config: from_attributes = True