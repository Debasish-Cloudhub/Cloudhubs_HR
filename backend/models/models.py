from sqlalchemy import Column, Integer, String, Date, DateTime, Float, Text, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base
import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"; manager = "manager"; employee = "employee"

class EmploymentTypeEnum(str, enum.Enum):
    permanent = "permanent"; contractor = "contractor"; intern = "intern"; consultant = "consultant"

class TimesheetStatusEnum(str, enum.Enum):
    pending = "pending"; approved = "approved"; rejected = "rejected"

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
    employment_type = Column(SAEnum(EmploymentTypeEnum), default=EmploymentTypeEnum.permanent)
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
    timesheets = relationship("Timesheet", back_populates="employee")
    salary_components = relationship("SalaryComponent", back_populates="employee")
    salary_records = relationship("SalaryRecord", back_populates="employee")

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
    basic = Column(Float, default=0); hra = Column(Float, default=0)
    allowances = Column(Float, default=0); bonus = Column(Float, default=0)
    pf_deduction = Column(Float, default=0); professional_tax = Column(Float, default=0)
    income_tax = Column(Float, default=0); effective_from = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    employee = relationship("Employee", back_populates="salary_components")

class SalaryRecord(Base):
    __tablename__ = "salary_records"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    month = Column(Integer); year = Column(Integer)
    basic = Column(Float, default=0); hra = Column(Float, default=0)
    allowances = Column(Float, default=0); bonus = Column(Float, default=0)
    gross_salary = Column(Float, default=0); pf_deduction = Column(Float, default=0)
    professional_tax = Column(Float, default=0); income_tax = Column(Float, default=0)
    total_deductions = Column(Float, default=0); net_salary = Column(Float, default=0)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    employee = relationship("Employee", back_populates="salary_records")

class Holiday(Base):
    __tablename__ = "holidays"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False); date = Column(Date, nullable=False)
    description = Column(Text, nullable=True); is_optional = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False); description = Column(Text, nullable=True)
    file_path = Column(String, nullable=False); file_name = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())