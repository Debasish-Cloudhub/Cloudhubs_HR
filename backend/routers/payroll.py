from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
from database.db import get_db
from models.models import User, Employee, SalaryComponent, SalaryRecord, RoleEnum
from schemas.schemas import SalaryComponentCreate, SalaryComponentOut, SalaryGenerateRequest, SalaryRecordOut
from utils.auth import get_current_user, require_admin
from utils.pdf_generator import generate_salary_slip
from datetime import date
from dateutil.relativedelta import relativedelta

router = APIRouter()

@router.post("/components", response_model=SalaryComponentOut)
def set_salary_components(data: SalaryComponentCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    comp = db.query(SalaryComponent).filter(SalaryComponent.employee_id == data.employee_id).first()
    if comp:
        for k, v in data.model_dump().items(): setattr(comp, k, v)
    else:
        comp = SalaryComponent(**data.model_dump()); db.add(comp)
    db.commit(); db.refresh(comp); return comp

@router.get("/components/{employee_id}", response_model=SalaryComponentOut)
def get_salary_components(employee_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    comp = db.query(SalaryComponent).filter(SalaryComponent.employee_id == employee_id).first()
    if not comp: raise HTTPException(status_code=404, detail="Not set")
    return comp

@router.post("/generate", response_model=SalaryRecordOut)
def generate_payslip(data: SalaryGenerateRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    comp = db.query(SalaryComponent).filter(SalaryComponent.employee_id == data.employee_id).first()
    if not comp: raise HTTPException(status_code=400, detail="Salary components not configured. Please set salary first.")
    existing = db.query(SalaryRecord).filter(
        SalaryRecord.employee_id == data.employee_id,
        SalaryRecord.month == data.month,
        SalaryRecord.year == data.year
    ).first()
    if existing: return existing
    gross = comp.basic + comp.hra + comp.allowances + comp.bonus
    deductions = comp.pf_deduction + comp.professional_tax + comp.income_tax
    rec = SalaryRecord(
        employee_id=data.employee_id, month=data.month, year=data.year,
        basic=comp.basic, hra=comp.hra, allowances=comp.allowances, bonus=comp.bonus,
        gross_salary=gross, pf_deduction=comp.pf_deduction,
        professional_tax=comp.professional_tax, income_tax=comp.income_tax,
        total_deductions=deductions, net_salary=gross - deductions
    )
    db.add(rec); db.commit(); db.refresh(rec); return rec

@router.post("/generate-all/{employee_id}")
def generate_all_from_joining(employee_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Generate payslips for every month from date of joining up to current month."""
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    comp = db.query(SalaryComponent).filter(SalaryComponent.employee_id == employee_id).first()
    if not comp: raise HTTPException(status_code=400, detail="Salary components not configured. Please set salary first.")
    if not emp.date_of_joining:
        raise HTTPException(status_code=400, detail="Employee has no date of joining set.")
    
    gross = comp.basic + comp.hra + comp.allowances + comp.bonus
    deductions = comp.pf_deduction + comp.professional_tax + comp.income_tax
    net = gross - deductions

    start = date(emp.date_of_joining.year, emp.date_of_joining.month, 1)
    today = date.today()
    current = start
    generated = []
    skipped = []

    while current <= today:
        existing = db.query(SalaryRecord).filter(
            SalaryRecord.employee_id == employee_id,
            SalaryRecord.month == current.month,
            SalaryRecord.year == current.year
        ).first()
        if not existing:
            rec = SalaryRecord(
                employee_id=employee_id, month=current.month, year=current.year,
                basic=comp.basic, hra=comp.hra, allowances=comp.allowances, bonus=comp.bonus,
                gross_salary=gross, pf_deduction=comp.pf_deduction,
                professional_tax=comp.professional_tax, income_tax=comp.income_tax,
                total_deductions=deductions, net_salary=net
            )
            db.add(rec)
            generated.append(f"{current.strftime('%b %Y')}")
        else:
            skipped.append(f"{current.strftime('%b %Y')}")
        current += relativedelta(months=1)

    db.commit()
    return {
        "message": f"Generated {len(generated)} payslips, skipped {len(skipped)} existing",
        "generated": generated,
        "skipped": skipped,
        "total": len(generated)
    }

@router.get("/records", response_model=List[SalaryRecordOut])
def list_salary_records(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == RoleEnum.admin:
        return db.query(SalaryRecord).order_by(SalaryRecord.year.desc(), SalaryRecord.month.desc()).all()
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp: return []
    return db.query(SalaryRecord).filter(
        SalaryRecord.employee_id == emp.id
    ).order_by(SalaryRecord.year.desc(), SalaryRecord.month.desc()).all()

@router.get("/slip/{record_id}")
def download_slip(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rec = db.query(SalaryRecord).filter(SalaryRecord.id == record_id).first()
    if not rec: raise HTTPException(status_code=404, detail="Not found")
    emp = db.query(Employee).filter(Employee.id == rec.employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    # Security: employee can only download their own slips
    if current_user.role.value == 'employee':
        my_emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not my_emp or my_emp.id != rec.employee_id:
            raise HTTPException(status_code=403, detail="Access denied")
    pdf = generate_salary_slip(emp, rec)
    fname = f"Payslip_{emp.employee_id}_{rec.month:02d}_{rec.year}.pdf"
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})
