from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import date, datetime
from models.models import RoleEnum, EmploymentTypeEnum, TimesheetStatusEnum, EmployeeStatusEnum

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
    lta: float = 0
    pf_deduction: float = 0
    professional_tax: float = 0
    income_tax: float = 0
    extra_earnings: List[Dict[str, float | str]] = []
    extra_deductions: List[Dict[str, float | str]] = []
    effective_from: Optional[date] = None

class SalaryComponentOut(BaseModel):
    id: int
    employee_id: int
    basic: float
    hra: float
    allowances: float
    bonus: float
    lta: float = 0
    pf_deduction: float
    professional_tax: float
    income_tax: float
    extra_earnings: Optional[str] = None
    extra_deductions: Optional[str] = None
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
    lta: float = 0
    gross_salary: float
    pf_deduction: float
    professional_tax: float
    income_tax: float
    misc_deductions: float = 0
    extra_earnings: Optional[str] = None
    extra_deductions: Optional[str] = None
    deduction_breakdown: Optional[str] = None
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


class MiscDeductionCreate(BaseModel):
    employee_id: int
    label: str
    amount: float
    month: int
    year: int
    remarks: Optional[str] = None

class MiscDeductionOut(BaseModel):
    id: int
    employee_id: int
    label: str
    amount: float
    month: int
    year: int
    remarks: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True


class AppraisalCreate(BaseModel):
    employee_id: int
    reviewer_id: Optional[int] = None
    assigned_manager_id: Optional[int] = None
    additional_reviewer_ids: List[int] = []
    appraisal_year: int
    period: str
    manager_feedback: Optional[str] = None
    additional_reviewer_feedback: Optional[str] = None
    overall_rating: Optional[float] = None
    comments: Optional[str] = None

class AppraisalUpdate(BaseModel):
    status: Optional[str] = None
    overall_rating: Optional[float] = None
    comments: Optional[str] = None
    reviewer_id: Optional[int] = None
    assigned_manager_id: Optional[int] = None
    additional_reviewer_ids: Optional[List[int]] = None
    appraisal_year: Optional[int] = None
    period: Optional[str] = None
    manager_feedback: Optional[str] = None
    additional_reviewer_feedback: Optional[str] = None
    salary_hike_percent: Optional[float] = None
    final_status: Optional[str] = None

class AppraisalOut(BaseModel):
    id: int
    employee_id: int
    reviewer_id: Optional[int] = None
    assigned_manager_id: Optional[int] = None
    additional_reviewer_ids: Optional[str] = None
    appraisal_year: Optional[int] = None
    period: str
    status: str
    manager_feedback: Optional[str] = None
    additional_reviewer_feedback: Optional[str] = None
    overall_rating: Optional[float] = None
    comments: Optional[str] = None
    salary_hike_percent: Optional[float] = None
    final_status: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True

class AppraisalGoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target: Optional[str] = None
    achievement: Optional[str] = None
    rating: Optional[float] = None

class AppraisalGoalOut(BaseModel):
    id: int
    appraisal_id: int
    title: str
    description: Optional[str] = None
    target: Optional[str] = None
    achievement: Optional[str] = None
    rating: Optional[float] = None
    created_at: datetime
    class Config:
        from_attributes = True

class AppraisalFeedbackCreate(BaseModel):
    strengths: Optional[str] = None
    improvements: Optional[str] = None
    overall_comment: Optional[str] = None
    rating: Optional[float] = None

class AppraisalFeedbackOut(BaseModel):
    id: int
    appraisal_id: int
    reviewer_id: int
    strengths: Optional[str] = None
    improvements: Optional[str] = None
    overall_comment: Optional[str] = None
    rating: Optional[float] = None
    created_at: datetime
    class Config:
        from_attributes = True
