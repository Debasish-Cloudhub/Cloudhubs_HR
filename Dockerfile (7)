from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base
import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    employee = "employee"
    manager = "manager"

class EmploymentTypeEnum(str, enum.Enum):
    permanent = "permanent"
    contractor = "contractor"
    intern = "intern"
    consultant = "consultant"

class TimesheetStatusEnum(str, enum.Enum):
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"

class TimesheetCategoryEnum(str, enum.Enum):
    development = "development"
    research = "research"
    admin = "admin"
    meeting = "meeting"
    support = "support"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.employee)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    employee = relationship("Employee", back_populates="user", uselist=False)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    employee_id = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    address = Column(Text)
    pan = Column(String)
    aadhaar = Column(String)
    bank_account = Column(String)
    bank_name = Column(String)
    ifsc = Column(String)
    pf_number = Column(String)
    uan = Column(String)
    date_of_joining = Column(Date)
    department = Column(String)
    designation = Column(String)
    location = Column(String)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    employment_type = Column(Enum(EmploymentTypeEnum), default=EmploymentTypeEnum.permanent)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="employee")
    manager = relationship("Employee", remote_side=[id])
    timesheets = relationship("Timesheet", back_populates="employee")
    salary_components = relationship("SalaryComponent", back_populates="employee")
    salary_records = relationship("SalaryRecord", back_populates="employee")

class Timesheet(Base):
    __tablename__ = "timesheets"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date, nullable=False)
    project_name = Column(String)
    task_description = Column(Text)
    hours_worked = Column(Float)
    category = Column(Enum(TimesheetCategoryEnum))
    status = Column(Enum(TimesheetStatusEnum), default=TimesheetStatusEnum.submitted)
    manager_comment = Column(Text)
    hr_comment = Column(Text)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    employee = relationship("Employee", back_populates="timesheets")

class SalaryComponent(Base):
    __tablename__ = "salary_components"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    basic = Column(Float, default=0)
    hra = Column(Float, default=0)
    allowances = Column(Float, default=0)
    bonus = Column(Float, default=0)
    pf = Column(Float, default=0)
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
    worked_days = Column(Integer)
    total_days = Column(Integer)
    lop_days = Column(Integer, default=0)
    basic = Column(Float, default=0)
    hra = Column(Float, default=0)
    allowances = Column(Float, default=0)
    bonus = Column(Float, default=0)
    gross_salary = Column(Float, default=0)
    pf = Column(Float, default=0)
    professional_tax = Column(Float, default=0)
    income_tax = Column(Float, default=0)
    total_deductions = Column(Float, default=0)
    net_salary = Column(Float, default=0)
    generated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="salary_records")

class Holiday(Base):
    __tablename__ = "holidays"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text)
    is_optional = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    filename = Column(String)
    filepath = Column(String)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
