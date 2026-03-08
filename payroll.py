from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.db import get_db
from models.models import User, Employee, Timesheet, SalaryRecord, Holiday, TimesheetStatusEnum, RoleEnum
from utils.auth import get_current_user, require_admin
from datetime import date

router = APIRouter()

@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    total_employees = db.query(Employee).filter(Employee.is_active == True).count()
    pending_timesheets = db.query(Timesheet).filter(Timesheet.status == TimesheetStatusEnum.submitted).count()
    today = date.today()
    upcoming_holidays = db.query(Holiday).filter(Holiday.date >= today).order_by(Holiday.date).limit(5).all()
    
    # Department breakdown
    dept_counts = db.query(
        Employee.department, func.count(Employee.id)
    ).filter(Employee.is_active == True).group_by(Employee.department).all()
    
    # Recent timesheets
    recent_ts = db.query(Timesheet).order_by(Timesheet.created_at.desc()).limit(10).all()

    return {
        "total_employees": total_employees,
        "pending_timesheets": pending_timesheets,
        "upcoming_holidays": [
            {"id": h.id, "name": h.name, "date": str(h.date), "is_optional": h.is_optional}
            for h in upcoming_holidays
        ],
        "department_breakdown": [
            {"department": d or "Unassigned", "count": c} for d, c in dept_counts
        ],
        "recent_timesheets": [
            {
                "id": ts.id,
                "employee_id": ts.employee_id,
                "date": str(ts.date),
                "project_name": ts.project_name,
                "hours_worked": ts.hours_worked,
                "status": ts.status.value
            } for ts in recent_ts
        ]
    }

@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp:
        return {"error": "Employee profile not found"}

    # This month's timesheets
    today = date.today()
    month_ts = db.query(Timesheet).filter(
        Timesheet.employee_id == emp.id,
        func.extract('month', Timesheet.date) == today.month,
        func.extract('year', Timesheet.date) == today.year
    ).all()

    total_hours = sum(ts.hours_worked for ts in month_ts)
    pending_ts = sum(1 for ts in month_ts if ts.status.value == 'submitted')

    # Recent salary records
    recent_salary = db.query(SalaryRecord).filter(
        SalaryRecord.employee_id == emp.id
    ).order_by(SalaryRecord.year.desc(), SalaryRecord.month.desc()).limit(3).all()

    # Upcoming holidays
    upcoming_holidays = db.query(Holiday).filter(
        Holiday.date >= today
    ).order_by(Holiday.date).limit(5).all()

    return {
        "employee": {
            "id": emp.id,
            "employee_id": emp.employee_id,
            "full_name": emp.full_name,
            "designation": emp.designation,
            "department": emp.department,
            "date_of_joining": str(emp.date_of_joining) if emp.date_of_joining else None
        },
        "this_month_hours": total_hours,
        "pending_timesheets": pending_ts,
        "recent_salary": [
            {"month": r.month, "year": r.year, "net_salary": r.net_salary, "id": r.id}
            for r in recent_salary
        ],
        "upcoming_holidays": [
            {"name": h.name, "date": str(h.date), "is_optional": h.is_optional}
            for h in upcoming_holidays
        ]
    }
