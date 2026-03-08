from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database.db import get_db
from models.models import User, Employee, Timesheet, TimesheetStatusEnum, RoleEnum
from schemas.schemas import TimesheetCreate, TimesheetOut, TimesheetUpdate
from utils.auth import get_current_user, require_admin

router = APIRouter()

@router.post("/submit", response_model=TimesheetOut)
def submit_timesheet(
    data: TimesheetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee profile not found")

    ts = Timesheet(
        employee_id=emp.id,
        date=data.date,
        project_name=data.project_name,
        task_description=data.task_description,
        hours_worked=data.hours_worked,
        category=data.category,
        status=TimesheetStatusEnum.submitted
    )
    db.add(ts)
    db.commit()
    db.refresh(ts)
    return ts

@router.get("/", response_model=List[TimesheetOut])
def list_timesheets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    employee_id: Optional[int] = None,
    status: Optional[TimesheetStatusEnum] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    q = db.query(Timesheet)
    
    if current_user.role == RoleEnum.employee:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not emp:
            return []
        q = q.filter(Timesheet.employee_id == emp.id)
    elif current_user.role == RoleEnum.manager:
        # Managers see their team's timesheets
        manager_emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if manager_emp:
            team = db.query(Employee).filter(Employee.manager_id == manager_emp.id).all()
            team_ids = [e.id for e in team]
            if manager_emp.id not in team_ids:
                team_ids.append(manager_emp.id)
            q = q.filter(Timesheet.employee_id.in_(team_ids))
    else:
        # Admin sees all, with optional filter
        if employee_id:
            q = q.filter(Timesheet.employee_id == employee_id)

    if status:
        q = q.filter(Timesheet.status == status)
    if from_date:
        q = q.filter(Timesheet.date >= from_date)
    if to_date:
        q = q.filter(Timesheet.date <= to_date)

    return q.order_by(Timesheet.date.desc()).all()

@router.put("/{ts_id}/approve", response_model=TimesheetOut)
def approve_timesheet(
    ts_id: int,
    data: TimesheetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [RoleEnum.admin, RoleEnum.manager]:
        raise HTTPException(status_code=403, detail="Not authorized")

    ts = db.query(Timesheet).filter(Timesheet.id == ts_id).first()
    if not ts:
        raise HTTPException(status_code=404, detail="Timesheet not found")

    ts.status = data.status
    if data.manager_comment:
        ts.manager_comment = data.manager_comment
    if data.hr_comment:
        ts.hr_comment = data.hr_comment
    ts.approved_by = current_user.id
    db.commit()
    db.refresh(ts)
    return ts

@router.delete("/{ts_id}")
def delete_timesheet(
    ts_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ts = db.query(Timesheet).filter(Timesheet.id == ts_id).first()
    if not ts:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if current_user.role == RoleEnum.employee:
        if not emp or emp.id != ts.employee_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        if ts.status != TimesheetStatusEnum.submitted:
            raise HTTPException(status_code=400, detail="Cannot delete approved/rejected timesheet")
    
    db.delete(ts)
    db.commit()
    return {"message": "Timesheet deleted"}
