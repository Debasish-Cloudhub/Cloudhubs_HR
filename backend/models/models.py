from sqlalchemy import Column, Integer, String, Date, DateTime, Float, Text, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base
import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    employee = "employee"

class EmploymentTypeEnum(str, enum.Enum):
    permanent = "permanent"
    contractor = "contractor"
    intern = "intern"
    consultant = "consultant"

class TimesheetStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class LeaveTypeEnum(str, enum.Enum):
    paid = "paid"
    sick = "sick"
    earned = "earned"
    sabbatical = "sabbatical"
    lop = "lop"

class LeaveStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class EmployeeStatusEnum(str, enum.Enum):
    active = "active"
    terminated = "terminated"
    resigned = "resigned"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(RoleEnum), default=RoleEnum.employee)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    employee = relationship("Employee", back_populates="user", uselist=False)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    employee_id = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    designation = Column(String)
    department = Column(String)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    employment_type = Column(SAEnum(EmploymentTypeEnum), default=EmploymentTypeEnum.permanent)
    status = Column(SAEnum(EmployeeStatusEnum), default=EmployeeStatusEnum.active)
    date_of_joining = Column(Date)
    date_of_birth = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    bank_account = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)
    pf_number = Column(String, nullable=True)
    uan_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="employee")
    manager = relationship("Employee", remote_side=[id], foreign_keys=[manager_id])
    timesheets = relationship("Timesheet", back_populates="employee")
    salary_components = relationship("SalaryComponent", back_populates="employee")
    salary_records = relationship("SalaryRecord", back_populates="employee")
    leave_requests = relationship("LeaveRequest", back_populates="employee", foreign_keys="LeaveRequest.employee_id")
    leave_balances = relationship("LeaveBalance", back_populates="employee")

class Timesheet(Base):
    __tablename__ = "timesheets"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date, nullable=False)
    hours_worked = Column(Float, default=8.0)
    task_description = Column(Text)
    project = Column(String, nullable=True)
    status = Column(SAEnum(TimesheetStatusEnum), default=TimesheetStatusEnum.pending)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    employee = relationship("Employee", back_populates="timesheets")

class SalaryComponent(Base):
    __tablename__ = "salary_components"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    basic = Column(Float, default=0)
    hra = Column(Float, default=0)
    allowances = Column(Float, default=0)
    bonus = Column(Float, default=0)
    pf_deduction = Column(Float, default=0)
    professional_tax = Column(Float, default=0)
    income_tax = Column(Float, default=0)
    effective_from = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    employee = relationship("Employee", back_populates="salary_components")

class SalaryRecord(Base):
    __tablename__ = "salary_records"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    month = Column(Integer)
    year = Column(Integer)
    basic = Column(Float, default=0)
    hra = Column(Float, default=0)
    allowances = Column(Float, default=0)
    bonus = Column(Float, default=0)
    gross_salary = Column(Float, default=0)
    pf_deduction = Column(Float, default=0)
    professional_tax = Column(Float, default=0)
    income_tax = Column(Float, default=0)
    total_deductions = Column(Float, default=0)
    net_salary = Column(Float, default=0)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    employee = relationship("Employee", back_populates="salary_records")

class Holiday(Base):
    __tablename__ = "holidays"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    is_optional = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LeaveConfig(Base):
    __tablename__ = "leave_config"
    id = Column(Integer, primary_key=True, index=True)
    leave_type = Column(SAEnum(LeaveTypeEnum), unique=True, nullable=False)
    days_per_year = Column(Integer, default=12)
    carry_forward = Column(Boolean, default=False)
    description = Column(String, nullable=True)

class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    leave_type = Column(SAEnum(LeaveTypeEnum), nullable=False)
    total_days = Column(Float, default=0)
    used_days = Column(Float, default=0)
    remaining_days = Column(Float, default=0)
    year = Column(Integer)
    employee = relationship("Employee", back_populates="leave_balances")

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    leave_type = Column(SAEnum(LeaveTypeEnum), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days = Column(Float, default=0)
    reason = Column(Text)
    status = Column(SAEnum(LeaveStatusEnum), default=LeaveStatusEnum.pending)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    employee = relationship("Employee", back_populates="leave_requests", foreign_keys=[employee_id])

class TerminationRecord(Base):
    __tablename__ = "termination_records"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    reason = Column(Text, nullable=False)
    termination_date = Column(Date, nullable=False)
    terminated_by = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ResignationRecord(Base):
    __tablename__ = "resignation_records"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    reason = Column(Text)
    notice_date = Column(Date, nullable=False)
    last_working_date = Column(Date, nullable=True)
    status = Column(String, default="pending")
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
