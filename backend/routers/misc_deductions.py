from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.db import get_db
from models.models import User, Employee, MiscDeduction, RoleEnum
from schemas.schemas import MiscDeductionCreate, MiscDeductionOut
from utils.auth import get_current_user, require_admin

router = APIRouter()

@router.post("/", response_model=MiscDeductionOut)
def create_misc_deduction(
    data: MiscDeductionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    deduction = MiscDeduction(**data.model_dump())
    db.add(deduction)
    db.commit()
    db.refresh(deduction)
    return deduction

@router.get("/{employee_id}", response_model=List[MiscDeductionOut])
def get_misc_deductions(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == RoleEnum.employee:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not emp or emp.id != employee_id:
            raise HTTPException(status_code=403, detail="Access denied")
    return db.query(MiscDeduction).filter(MiscDeduction.employee_id == employee_id).all()

@router.delete("/{deduction_id}")
def delete_misc_deduction(
    deduction_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    deduction = db.query(MiscDeduction).filter(MiscDeduction.id == deduction_id).first()
    if not deduction:
        raise HTTPException(status_code=404, detail="Deduction not found")
    db.delete(deduction)
    db.commit()
    return {"message": "Deduction deleted successfully"}
