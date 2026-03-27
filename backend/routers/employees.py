from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.db import get_db
from models.models import User, Employee, RoleEnum
from schemas.schemas import EmployeeCreate, EmployeeOut
from utils.auth import get_current_user, require_admin, hash_password
from utils.employee_id import generate_employee_id
router = APIRouter()
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