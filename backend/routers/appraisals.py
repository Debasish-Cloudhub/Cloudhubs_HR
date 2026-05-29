from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
from database.db import get_db
from models.models import User, Employee, Appraisal, AppraisalReviewer, AppraisalStatusEnum
from schemas.schemas import AppraisalCreate, AppraisalApprove, AppraisalOut, ReviewerAdd, ReviewerFeedback, AppraisalReviewerOut
from utils.auth import get_current_user, require_admin, require_admin_or_manager
from utils.pdf_generator import generate_appraisal_pdf

router = APIRouter()

def _appraisal_to_out(a):
    emp = a.employee
    emp_name = f"{emp.first_name} {emp.last_name}" if emp else None
    mgr = a.manager
    mgr_email = mgr.email if mgr else None
    reviewers = []
    for rv in a.reviewers:
        rev_emp = rv.reviewer
        rname = f"{rev_emp.first_name} {rev_emp.last_name}" if rev_emp else None
        reviewers.append(AppraisalReviewerOut(
            id=rv.id, reviewer_id=rv.reviewer_id,
            reviewer_name=rname, feedback=rv.feedback, rating=rv.rating
        ))
    return AppraisalOut(
        id=a.id, employee_id=a.employee_id, employee_name=emp_name,
        manager_id=a.manager_id, manager_email=mgr_email,
        year=a.year, period=a.period,
        manager_feedback=a.manager_feedback,
        salary_hike_percent=a.salary_hike_percent,
        final_status=a.final_status,
        reviewers=reviewers,
        created_at=a.created_at
    )

@router.post("/", response_model=AppraisalOut)
def create_appraisal(data: AppraisalCreate, db: Session = Depends(get_db), user: User = Depends(require_admin_or_manager)):
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    # Check for duplicate
    existing = db.query(Appraisal).filter(
        Appraisal.employee_id == data.employee_id,
        Appraisal.year == data.year,
        Appraisal.period == data.period
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Appraisal already exists for this employee/year/period")
    appraisal = Appraisal(
        employee_id=data.employee_id,
        manager_id=data.manager_id,
        year=data.year,
        period=data.period,
        manager_feedback=data.manager_feedback
    )
    db.add(appraisal)
    db.commit()
    db.refresh(appraisal)
    return _appraisal_to_out(appraisal)

@router.get("/", response_model=List[AppraisalOut])
def list_appraisals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role.value == 'employee':
        emp = db.query(Employee).filter(Employee.user_id == user.id).first()
        if not emp:
            return []
        appraisals = db.query(Appraisal).filter(
            Appraisal.employee_id == emp.id,
            Appraisal.final_status == AppraisalStatusEnum.approved
        ).order_by(Appraisal.year.desc()).all()
    else:
        appraisals = db.query(Appraisal).order_by(Appraisal.year.desc()).all()
    return [_appraisal_to_out(a) for a in appraisals]

@router.get("/{appraisal_id}", response_model=AppraisalOut)
def get_appraisal(appraisal_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    a = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    return _appraisal_to_out(a)

@router.put("/{appraisal_id}", response_model=AppraisalOut)
def update_appraisal(appraisal_id: int, data: AppraisalCreate, db: Session = Depends(get_db), user: User = Depends(require_admin_or_manager)):
    a = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    if a.final_status == AppraisalStatusEnum.approved:
        raise HTTPException(status_code=400, detail="Cannot edit an approved appraisal")
    a.manager_feedback = data.manager_feedback
    a.manager_id = data.manager_id
    db.commit()
    db.refresh(a)
    return _appraisal_to_out(a)

@router.post("/{appraisal_id}/reviewers", response_model=AppraisalOut)
def add_reviewer(appraisal_id: int, data: ReviewerAdd, db: Session = Depends(get_db), user: User = Depends(require_admin_or_manager)):
    a = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    rev_emp = db.query(Employee).filter(Employee.id == data.reviewer_id).first()
    if not rev_emp:
        raise HTTPException(status_code=404, detail="Reviewer employee not found")
    # Check duplicate reviewer
    existing = db.query(AppraisalReviewer).filter(
        AppraisalReviewer.appraisal_id == appraisal_id,
        AppraisalReviewer.reviewer_id == data.reviewer_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Reviewer already added")
    reviewer = AppraisalReviewer(appraisal_id=appraisal_id, reviewer_id=data.reviewer_id)
    db.add(reviewer)
    db.commit()
    db.refresh(a)
    return _appraisal_to_out(a)

@router.put("/{appraisal_id}/reviewers/{reviewer_id}/feedback")
def submit_reviewer_feedback(appraisal_id: int, reviewer_id: int, data: ReviewerFeedback, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rv = db.query(AppraisalReviewer).filter(
        AppraisalReviewer.appraisal_id == appraisal_id,
        AppraisalReviewer.reviewer_id == reviewer_id
    ).first()
    if not rv:
        raise HTTPException(status_code=404, detail="Reviewer not found for this appraisal")
    rv.feedback = data.feedback
    rv.rating = data.rating
    db.commit()
    return {"message": "Feedback submitted"}

@router.patch("/{appraisal_id}/approve", response_model=AppraisalOut)
def approve_appraisal(appraisal_id: int, data: AppraisalApprove, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    a = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    a.final_status = data.final_status
    a.salary_hike_percent = data.salary_hike_percent
    db.commit()
    db.refresh(a)
    return _appraisal_to_out(a)

@router.delete("/{appraisal_id}")
def delete_appraisal(appraisal_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    a = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    db.delete(a)
    db.commit()
    return {"message": "Appraisal deleted"}

@router.get("/{appraisal_id}/pdf")
def download_appraisal_pdf(appraisal_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    a = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    if a.final_status != AppraisalStatusEnum.approved:
        raise HTTPException(status_code=400, detail="Appraisal must be approved before downloading PDF")
    # Security: employees can only download their own
    if user.role.value == 'employee':
        emp = db.query(Employee).filter(Employee.user_id == user.id).first()
        if not emp or emp.id != a.employee_id:
            raise HTTPException(status_code=403, detail="Access denied")
    emp = a.employee
    reviewers_data = []
    for rv in a.reviewers:
        rev_emp = rv.reviewer
        reviewers_data.append({
            'name': f"{rev_emp.first_name} {rev_emp.last_name}" if rev_emp else 'Unknown',
            'feedback': rv.feedback or '-',
            'rating': rv.rating
        })
    pdf = generate_appraisal_pdf(emp, a, reviewers_data)
    fname = f"Appraisal_{emp.employee_id}_{a.year}_{a.period.value}.pdf"
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})
