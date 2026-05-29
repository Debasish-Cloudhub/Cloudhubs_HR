from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from models.models import RoleEnum, EmploymentTypeEnum, TimesheetStatusEnum, EmployeeStatusEnum, AppraisalPeriodEnum, AppraisalStatusEnum

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int

class EmployeeCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    employment_type: EmploymentTypeEnum = EmploymentTypeEnum.permanent
    date_of_joining: Optional[date] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    pf_number: Optional[str] = None
    uan_number: Optional[str] = None

class EmployeeOut(BaseModel):
    id: int
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    employment_type: EmploymentTypeEnum
    status: Optional[EmployeeStatusEnum] = EmployeeStatusEnum.active
    manager_id: Optional[int] = None
    date_of_joining: Optional[date] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    pf_number: Optional[str] = None
    uan_number: Optional[str] = None
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class TimesheetCreate(BaseModel):
    date: date
    hours_worked: float = 8.0
    task_description: Optional[str] = None
    project: Optional[str] = None

class TimesheetApprove(BaseModel):
    status: TimesheetStatusEnum
    rejection_reason: Optional[str] = None

class TimesheetOut(BaseModel):
    id: int
    date: date
    hours_worked: float
    task_description: Optional[str] = None
    project: Optional[str] = None
    status: TimesheetStatusEnum
    rejection_reason: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class SalaryComponentCreate(BaseModel):
    employee_id: int
    basic: float = 0
    hra: float = 0
    allowances: float = 0
    bonus: float = 0
    pf_deduction: float = 0
    professional_tax: float = 0
    income_tax: float = 0
    lta: float = 0
    effective_from: Optional[date] = None

class SalaryComponentOut(BaseModel):
    id: int
    employee_id: int
    basic: float
    hra: float
    allowances: float
    bonus: float
    pf_deduction: float
    professional_tax: float
    income_tax: float
    lta: float
    effective_from: Optional[date] = None
    class Config:
        from_attributes = True

class SalaryGenerateRequest(BaseModel):
    employee_id: int
    month: int
    year: int

class SalaryRecordOut(BaseModel):
    id: int
    employee_id: int
    month: int
    year: int
    basic: float
    hra: float
    allowances: float
    bonus: float
    gross_salary: float
    pf_deduction: float
    professional_tax: float
    income_tax: float
    total_deductions: float
    net_salary: float
    generated_at: datetime
    class Config:
        from_attributes = True

class HolidayCreate(BaseModel):
    name: str
    date: date
    description: Optional[str] = None
    is_optional: bool = False

class HolidayOut(BaseModel):
    id: int
    name: str
    date: date
    description: Optional[str] = None
    is_optional: bool
    class Config:
        from_attributes = True

class DocumentOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    file_name: str
    is_public: bool
    created_at: datetime
    class Config:
        from_attributes = True

# ── Appraisal Schemas ──
class AppraisalCreate(BaseModel):
    employee_id: int
    manager_id: int
    year: int
    period: AppraisalPeriodEnum
    manager_feedback: Optional[str] = None

class AppraisalApprove(BaseModel):
    salary_hike_percent: Optional[float] = None
    final_status: AppraisalStatusEnum

class ReviewerAdd(BaseModel):
    reviewer_id: int

class ReviewerFeedback(BaseModel):
    feedback: Optional[str] = None
    rating: Optional[int] = None

class AppraisalReviewerOut(BaseModel):
    id: int
    reviewer_id: int
    reviewer_name: Optional[str] = None
    feedback: Optional[str] = None
    rating: Optional[int] = None
    class Config:
        from_attributes = True

class AppraisalOut(BaseModel):
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    manager_id: int
    manager_email: Optional[str] = None
    year: int
    period: AppraisalPeriodEnum
    manager_feedback: Optional[str] = None
    salary_hike_percent: Optional[float] = None
    final_status: AppraisalStatusEnum
    reviewers: List[AppraisalReviewerOut] = []
    created_at: datetime
    class Config:
        from_attributes = True

# ── Misc Deduction Schemas ──
class MiscDeductionCreate(BaseModel):
    employee_id: int
    month: int
    year: int
    deduction_head: str
    amount: float

class MiscDeductionOut(BaseModel):
    id: int
    employee_id: int
    month: int
    year: int
    deduction_head: str
    amount: float
    created_at: datetime
    class Config:
        from_attributes = True
