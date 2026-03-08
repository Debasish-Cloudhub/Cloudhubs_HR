from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from models.models import User, Employee, RoleEnum
from schemas.schemas import EmployeeCreate, EmployeeOut, EmployeeUpdate
from utils.auth import get_current_user, require_admin, hash_password
from utils.employee_id import generate_employee_id

router = APIRouter()

@router.post("/", response_model=EmployeeOut)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    # Check email
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user account
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=RoleEnum.employee
    )
    db.add(user)
    db.flush()

    # Generate employee ID
    emp_id = generate_employee_id(db, data.employment_type)

    employee = Employee(
        user_id=user.id,
        employee_id=emp_id,
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        address=data.address,
        pan=data.pan,
        aadhaar=data.aadhaar,
        bank_account=data.bank_account,
        bank_name=data.bank_name,
        ifsc=data.ifsc,
        pf_number=data.pf_number,
        uan=data.uan,
        date_of_joining=data.date_of_joining,
        department=data.department,
        designation=data.designation,
        location=data.location,
        manager_id=data.manager_id,
        employment_type=data.employment_type
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

@router.get("/", response_model=List[EmployeeOut])
def list_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: Optional[str] = None,
    department: Optional[str] = None,
    active_only: bool = True
):
    if current_user.role not in [RoleEnum.admin, RoleEnum.manager]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    q = db.query(Employee)
    if active_only:
        q = q.filter(Employee.is_active == True)
    if search:
        q = q.filter(Employee.full_name.ilike(f"%{search}%"))
    if department:
        q = q.filter(Employee.department == department)
    return q.all()

@router.get("/me", response_model=EmployeeOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return emp

@router.get("/{emp_id}", response_model=EmployeeOut)
def get_employee(
    emp_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Employees can only see themselves
    if current_user.role == RoleEnum.employee:
        own_emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not own_emp or own_emp.id != emp_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    return emp

@router.put("/{emp_id}", response_model=EmployeeOut)
def update_employee(
    emp_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Only admin can update sensitive fields; employee can update limited fields
    if current_user.role == RoleEnum.employee:
        own_emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not own_emp or own_emp.id != emp_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        # Limited fields for self-update
        for field in ['phone', 'address', 'bank_account', 'bank_name', 'ifsc']:
            val = getattr(data, field, None)
            if val is not None:
                setattr(emp, field, val)
    else:
        for field, val in data.model_dump(exclude_unset=True).items():
            setattr(emp, field, val)

    db.commit()
    db.refresh(emp)
    return emp

@router.delete("/{emp_id}")
def deactivate_employee(
    emp_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.is_active = False
    db.commit()
    return {"message": "Employee deactivated"}
