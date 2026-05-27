from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
from database.db import get_db
from models.models import User, Employee, Appraisal, AppraisalGoal, AppraisalFeedback, RoleEnum, AppraisalStatusEnum
from schemas.schemas import (
    AppraisalCreate, AppraisalOut, AppraisalUpdate,
    AppraisalGoalCreate, AppraisalGoalOut,
    AppraisalFeedbackCreate, AppraisalFeedbackOut
)
from utils.auth import get_current_user, require_admin, require_admin_or_manager
from utils.pdf_generator import generate_appraisal_report

router = APIRouter()

def _reviewer_ids_json(ids):
    return json.dumps([int(x) for x in (ids or []) if x])

def _reviewer_ids(value):
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []

def _get_reviewers(db, appraisal):
    ids = _reviewer_ids(appraisal.additional_reviewer_ids)
    if not ids:
        return []
    return db.query(Employee).filter(Employee.id.in_(ids)).all()

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
    payload = data.model_dump()
    payload["additional_reviewer_ids"] = _reviewer_ids_json(payload.pop("additional_reviewer_ids", []))
    if not payload.get("assigned_manager_id"):
        payload["assigned_manager_id"] = emp.manager_id
    appraisal = Appraisal(**payload)
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
    return db.query(Appraisal).order_by(Appraisal.created_at.desc()).all()

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
    payload = data.model_dump(exclude_unset=True)
    if "additional_reviewer_ids" in payload:
        payload["additional_reviewer_ids"] = _reviewer_ids_json(payload["additional_reviewer_ids"])
    for key, value in payload.items():
        setattr(appraisal, key, value)
    db.commit()
    db.refresh(appraisal)
    return appraisal

@router.put("/{appraisal_id}/approve", response_model=AppraisalOut)
def approve_appraisal(
    appraisal_id: int,
    data: AppraisalUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    payload = data.model_dump(exclude_unset=True)
    for key in ["salary_hike_percent", "final_status", "overall_rating", "comments", "manager_feedback", "additional_reviewer_feedback"]:
        if key in payload:
            setattr(appraisal, key, payload[key])
    appraisal.status = AppraisalStatusEnum.approved
    appraisal.approved_by = admin.id
    appraisal.approved_at = datetime.utcnow()
    if not appraisal.final_status:
        appraisal.final_status = "Approved"
    db.commit()
    db.refresh(appraisal)
    return appraisal

@router.get("/{appraisal_id}/pdf")
def download_appraisal_pdf(
    appraisal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    emp = db.query(Employee).filter(Employee.id == appraisal.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    if current_user.role == RoleEnum.employee:
        my_emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not my_emp or my_emp.id != appraisal.employee_id:
            raise HTTPException(status_code=403, detail="Access denied")
        if appraisal.status != AppraisalStatusEnum.approved:
            raise HTTPException(status_code=403, detail="Appraisal report is available after HR approval")
    manager = db.query(Employee).filter(Employee.id == appraisal.assigned_manager_id).first() if appraisal.assigned_manager_id else None
    pdf = generate_appraisal_report(emp, appraisal, manager, _get_reviewers(db, appraisal))
    fname = f"Appraisal_{emp.employee_id}_{appraisal.appraisal_year or 'Report'}.pdf"
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})

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
