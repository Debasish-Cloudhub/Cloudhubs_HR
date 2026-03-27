from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from models.models import User, Holiday
from schemas.schemas import HolidayCreate, HolidayOut
from utils.auth import get_current_user, require_admin
router = APIRouter()
@router.post("/", response_model=HolidayOut)
def create_holiday(data: HolidayCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    h = Holiday(**data.model_dump()); db.add(h); db.commit(); db.refresh(h); return h
@router.get("/", response_model=List[HolidayOut])
def list_holidays(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), year: Optional[int] = None):
    q = db.query(Holiday)
    if year:
        from sqlalchemy import extract
        q = q.filter(extract('year', Holiday.date) == year)
    return q.order_by(Holiday.date.asc()).all()
@router.delete("/{holiday_id}")
def delete_holiday(holiday_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    h = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not h: raise HTTPException(status_code=404, detail="Not found")
    db.delete(h); db.commit(); return {"message": "Deleted"}