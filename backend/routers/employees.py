from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from models.models import User, Employee, RoleEnum, TerminationRecord, ResignationRecord, EmployeeStatusEnum
from schemas.schemas import EmployeeCreate, EmployeeOut
from utils.auth import get_current_user, require_admin, hash_password
from utils.employee_id import generate_employee_id
from pydantic import BaseModel
from datetime import date

router = APIRouter()

class TerminateRequest(BaseModel):
    reason: str
    termination_date: date
    notes: Optional[str] = None

class ResignRequest(BaseModel):
    reason: Optional[str] = None
    notice_date: date
    last_working_date: Optional[date] = None

class AssignManagerRequest(BaseModel):
    manager_employee_id: int

class CreateAdminRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

@router.post("/", response_model=EmployeeOut)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, hashed_password=hash_password(data.password), role=RoleEnum.employee)
    db.add(user); db.flush()
    emp_id = generate_employee_id(db, data.employment_type)
    emp = Employee(user_id=user.id, employee_id=emp_id, first_name=data.first_name, last_name=data.last_name, email=data.email, phone=data.phone, designation=data.designation, department=data.department, employment_type=data.employment_type, date_of_joining=data.date_of_joining, date_of_birth=data.date_of_birth, address=data.address, bank_account=data.bank_account, bank_name=data.bank_name, ifsc_code=data.ifsc_code, pf_number=data.pf_number, uan_number=data.uan_number)
    db.add(emp); db.commit(); db.refresh(emp); return emp

@router.get("/", response_model=List[EmployeeOut])
def list_employees(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(Employee).filter(Employee.is_active == True).all()

@router.get("/me", response_model=EmployeeOut)
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp: raise HTTPException(status_code=404, detail="Profile not found")
    return emp

@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Not found")
    return emp

@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    user = db.query(User).filter(User.id == emp.user_id).first()
    if user: user.is_active = False
    emp.is_active = False
    db.commit()
    return {"message": "Employee deleted"}

@router.post("/{employee_id}/terminate")
def terminate_employee(employee_id: int, data: TerminateRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    emp.status = EmployeeStatusEnum.terminated
    emp.is_active = False
    user = db.query(User).filter(User.id == emp.user_id).first()
    if user: user.is_active = False
    rec = TerminationRecord(employee_id=emp.id, reason=data.reason, termination_date=data.termination_date, terminated_by=admin.id, notes=data.notes)
    db.add(rec); db.commit()
    return {"message": "Employee terminated", "employee_id": emp.employee_id}

@router.post("/{employee_id}/assign-manager")
def assign_manager(employee_id: int, data: AssignManagerRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    mgr = db.query(Employee).filter(Employee.id == data.manager_employee_id).first()
    if not mgr: raise HTTPException(status_code=404, detail="Manager not found")
    emp.manager_id = mgr.id
    db.commit()
    return {"message": "Manager assigned", "manager": mgr.first_name + " " + mgr.last_name}

@router.post("/admin/create")
def create_admin(data: CreateAdminRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    new_admin = User(email=data.email, hashed_password=hash_password(data.password), role=RoleEnum.admin)
    db.add(new_admin); db.flush()
    emp_id = generate_employee_id(db, "permanent")
    from models.models import EmploymentTypeEnum
    emp = Employee(user_id=new_admin.id, employee_id=emp_id, first_name=data.first_name, last_name=data.last_name, email=data.email, employment_type=EmploymentTypeEnum.permanent)
    db.add(emp); db.commit()
    return {"message": "Admin created", "email": data.email}

@router.post("/me/resign")
def apply_resignation(data: ResignRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    rec = ResignationRecord(employee_id=emp.id, reason=data.reason, notice_date=data.notice_date, last_working_date=data.last_working_date)
    db.add(rec); db.commit(); db.refresh(rec)
    return {"message": "Resignation submitted", "id": rec.id}

@router.get("/resignations/all")
def all_resignations(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    recs = db.query(ResignationRecord).order_by(ResignationRecord.created_at.desc()).all()
    return [{"id": r.id, "employee_id": r.employee_id, "reason": r.reason, "notice_date": str(r.notice_date), "status": r.status, "created_at": str(r.created_at)} for r in recs]
