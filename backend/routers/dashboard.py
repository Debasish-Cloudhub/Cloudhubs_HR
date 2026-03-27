from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from models.models import User, Employee, Timesheet, Holiday, TimesheetStatusEnum
from utils.auth import require_admin
from datetime import date
router = APIRouter()
@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return {
        "total_employees": db.query(Employee).filter(Employee.is_active == True).count(),
        "pending_timesheets": db.query(Timesheet).filter(Timesheet.status == TimesheetStatusEnum.pending).count(),
        "approved_timesheets": db.query(Timesheet).filter(Timesheet.status == TimesheetStatusEnum.approved).count(),
        "upcoming_holidays": [{"name": h.name, "date": str(h.date)} for h in db.query(Holiday).filter(Holiday.date >= date.today()).order_by(Holiday.date).limit(5).all()]
    }