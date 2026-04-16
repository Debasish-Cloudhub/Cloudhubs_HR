from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from models.models import User, Employee, LeaveRequest, LeaveBalance, LeaveConfig, LeaveTypeEnum, LeaveStatusEnum, RoleEnum
from utils.auth import get_current_user, require_admin, require_admin_or_manager
from pydantic import BaseModel
from datetime import date
import datetime

router = APIRouter()

class LeaveRequestCreate(BaseModel):
    leave_type: LeaveTypeEnum
    start_date: date
    end_date: date
    reason: Optional[str] = None

class LeaveReview(BaseModel):
    status: LeaveStatusEnum
    review_comment: Optional[str] = None

class LeaveRequestOut(BaseModel):
    id: int
    employee_id: int
    leave_type: LeaveTypeEnum
    start_date: date
    end_date: date
    days: float
    reason: Optional[str]
    status: LeaveStatusEnum
    review_comment: Optional[str]
    created_at: datetime.datetime
    class Config: from_attributes = True

class LeaveBalanceOut(BaseModel):
    id: int
    employee_id: int
    leave_type: LeaveTypeEnum
    total_days: float
    used_days: float
    remaining_days: float
    year: int
    class Config: from_attributes = True

class LeaveConfigOut(BaseModel):
    id: int
    leave_type: LeaveTypeEnum
    days_per_year: int
    carry_forward: bool
    description: Optional[str]
    class Config: from_attributes = True

class LeaveConfigCreate(BaseModel):
    leave_type: LeaveTypeEnum
    days_per_year: int
    carry_forward: bool = False
    description: Optional[str] = None

@router.post("/request", response_model=LeaveRequestOut)
def apply_leave(data: LeaveRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee profile not found")
    delta = (data.end_date - data.start_date).days + 1
    req = LeaveRequest(employee_id=emp.id, leave_type=data.leave_type, start_date=data.start_date, end_date=data.end_date, days=delta, reason=data.reason)
    db.add(req); db.commit(); db.refresh(req); return req

@router.get("/my", response_model=List[LeaveRequestOut])
def my_leaves(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp: return []
    return db.query(LeaveRequest).filter(LeaveRequest.employee_id == emp.id).order_by(LeaveRequest.created_at.desc()).all()

@router.get("/all", response_model=List[LeaveRequestOut])
def all_leaves(db: Session = Depends(get_db), current_user: User = Depends(require_admin_or_manager)):
    return db.query(LeaveRequest).order_by(LeaveRequest.created_at.desc()).all()

@router.put("/{leave_id}/review")
def review_leave(leave_id: int, data: LeaveReview, db: Session = Depends(get_db), current_user: User = Depends(require_admin_or_manager)):
    req = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not req: raise HTTPException(status_code=404, detail="Leave request not found")
    req.status = data.status
    req.reviewed_by = current_user.id
    req.review_comment = data.review_comment
    db.commit()
    return {"message": f"Leave {data.status.value}"}

@router.get("/balances/my", response_model=List[LeaveBalanceOut])
def my_balance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp: return []
    return db.query(LeaveBalance).filter(LeaveBalance.employee_id == emp.id, LeaveBalance.year == date.today().year).all()

@router.get("/config", response_model=List[LeaveConfigOut])
def get_config(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(LeaveConfig).all()

@router.post("/config", response_model=LeaveConfigOut)
def set_config(data: LeaveConfigCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    existing = db.query(LeaveConfig).filter(LeaveConfig.leave_type == data.leave_type).first()
    if existing:
        existing.days_per_year = data.days_per_year
        existing.carry_forward = data.carry_forward
        existing.description = data.description
        db.commit(); db.refresh(existing); return existing
    cfg = LeaveConfig(**data.model_dump())
    db.add(cfg); db.commit(); db.refresh(cfg); return cfg
