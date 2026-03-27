from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.db import get_db
from models.models import User, Employee, Timesheet, TimesheetStatusEnum, RoleEnum
from schemas.schemas import TimesheetCreate, TimesheetApprove, TimesheetOut
from utils.auth import get_current_user, require_admin_or_manager
router = APIRouter()
@router.post("/submit", response_model=TimesheetOut)
def submit_timesheet(data: TimesheetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee profile not found")
    if db.query(Timesheet).filter(Timesheet.employee_id == emp.id, Timesheet.date == data.date).first():
        raise HTTPException(status_code=400, detail="Already submitted for this date")
    ts = Timesheet(employee_id=emp.id, **data.model_dump())
    db.add(ts); db.commit(); db.refresh(ts); return ts
@router.get("/", response_model=List[TimesheetOut])
def list_timesheets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role in [RoleEnum.admin, RoleEnum.manager]:
        return db.query(Timesheet).order_by(Timesheet.date.desc()).all()
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    return db.query(Timesheet).filter(Timesheet.employee_id == emp.id).order_by(Timesheet.date.desc()).all() if emp else []
@router.put("/{ts_id}/approve")
def approve_timesheet(ts_id: int, data: TimesheetApprove, db: Session = Depends(get_db), current_user: User = Depends(require_admin_or_manager)):
    ts = db.query(Timesheet).filter(Timesheet.id == ts_id).first()
    if not ts: raise HTTPException(status_code=404, detail="Not found")
    ts.status = data.status; ts.approved_by = current_user.id
    if data.rejection_reason: ts.rejection_reason = data.rejection_reason
    db.commit(); return {"message": f"Timesheet {data.status.value}"}