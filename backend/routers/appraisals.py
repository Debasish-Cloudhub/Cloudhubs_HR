from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from models.models import User, Employee, Appraisal, AppraisalGoal, AppraisalFeedback, RoleEnum
from schemas.schemas import (
    AppraisalCreate, AppraisalOut, AppraisalUpdate,
    AppraisalGoalCreate, AppraisalGoalOut,
    AppraisalFeedbackCreate, AppraisalFeedbackOut
)
from utils.auth import get_current_user, require_admin, require_admin_or_manager

router = APIRouter()

# ── APPRAISALS ──────────────────────────────────────────────────────────────

@router.post("/", response_model=AppraisalOut)
def create_appraisal(
    data: AppraisalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager)
):
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    appraisal = Appraisal(**data.model_dump())
    db.add(appraisal)
    db.commit()
    db.refresh(appraisal)
    return appraisal

@router.get("/", response_model=List[AppraisalOut])
def list_appraisals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == RoleEnum.employee:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not emp:
            return []
        return db.query(Appraisal).filter(Appraisal.employee_id == emp.id).all()
    return db.query(Appraisal).all()

@router.get("/{appraisal_id}", response_model=AppraisalOut)
def get_appraisal(
    appraisal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    if current_user.role == RoleEnum.employee:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not emp or emp.id != appraisal.employee_id:
            raise HTTPException(status_code=403, detail="Access denied")
    return appraisal

@router.put("/{appraisal_id}", response_model=AppraisalOut)
def update_appraisal(
    appraisal_id: int,
    data: AppraisalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager)
):
    appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(appraisal, key, value)
    db.commit()
    db.refresh(appraisal)
    return appraisal

@router.delete("/{appraisal_id}")
def delete_appraisal(
    appraisal_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    db.delete(appraisal)
    db.commit()
    return {"message": "Appraisal deleted"}

# ── GOALS ────────────────────────────────────────────────────────────────────

@router.post("/{appraisal_id}/goals", response_model=AppraisalGoalOut)
def add_goal(
    appraisal_id: int,
    data: AppraisalGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    goal = AppraisalGoal(appraisal_id=appraisal_id, **data.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

@router.get("/{appraisal_id}/goals", response_model=List[AppraisalGoalOut])
def list_goals(
    appraisal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(AppraisalGoal).filter(AppraisalGoal.appraisal_id == appraisal_id).all()

@router.delete("/goals/{goal_id}")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager)
):
    goal = db.query(AppraisalGoal).filter(AppraisalGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted"}

# ── FEEDBACK ─────────────────────────────────────────────────────────────────

@router.post("/{appraisal_id}/feedback", response_model=AppraisalFeedbackOut)
def add_feedback(
    appraisal_id: int,
    data: AppraisalFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    feedback = AppraisalFeedback(
        appraisal_id=appraisal_id,
        reviewer_id=current_user.id,
        **data.model_dump()
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback

@router.get("/{appraisal_id}/feedback", response_model=List[AppraisalFeedbackOut])
def list_feedback(
    appraisal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(AppraisalFeedback).filter(AppraisalFeedback.appraisal_id == appraisal_id).all()
