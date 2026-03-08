from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from models.models import User, Employee, SalaryComponent, SalaryRecord, RoleEnum
from schemas.schemas import SalaryComponentCreate, SalaryComponentOut, SalaryGenerateRequest, SalaryRecordOut
from utils.auth import get_current_user, require_admin
from utils.pdf_generator import generate_salary_slip

router = APIRouter()

@router.post("/components", response_model=SalaryComponentOut)
def set_salary_components(
    data: SalaryComponentCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    comp = SalaryComponent(
        employee_id=data.employee_id,
        basic=data.basic,
        hra=data.hra,
        allowances=data.allowances,
        bonus=data.bonus,
        pf=data.pf,
        professional_tax=data.professional_tax,
        income_tax=data.income_tax,
        effective_from=data.effective_from
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return comp

@router.get("/components/{employee_id}", response_model=Optional[SalaryComponentOut])
def get_salary_components(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == RoleEnum.employee:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not emp or emp.id != employee_id:
            raise HTTPException(status_code=403, detail="Not authorized")

    comp = db.query(SalaryComponent).filter(
        SalaryComponent.employee_id == employee_id
    ).order_by(SalaryComponent.effective_from.desc()).first()
    return comp

@router.post("/generate", response_model=SalaryRecordOut)
def generate_payroll(
    data: SalaryGenerateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    comp = db.query(SalaryComponent).filter(
        SalaryComponent.employee_id == data.employee_id
    ).order_by(SalaryComponent.effective_from.desc()).first()
    if not comp:
        raise HTTPException(status_code=400, detail="No salary components defined for this employee")

    # Check if already generated
    existing = db.query(SalaryRecord).filter(
        SalaryRecord.employee_id == data.employee_id,
        SalaryRecord.month == data.month,
        SalaryRecord.year == data.year
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Salary already generated for this period")

    # Calculate proportional salary based on worked days
    ratio = data.worked_days / data.total_days if data.total_days > 0 else 0

    basic = round(comp.basic * ratio, 2)
    hra = round(comp.hra * ratio, 2)
    allowances = round(comp.allowances * ratio, 2)
    bonus = round(comp.bonus * ratio, 2)
    gross = round(basic + hra + allowances + bonus, 2)

    pf = round(comp.pf, 2)
    pt = round(comp.professional_tax, 2)
    it = round(comp.income_tax, 2)
    total_ded = round(pf + pt + it, 2)
    net = round(gross - total_ded, 2)

    record = SalaryRecord(
        employee_id=data.employee_id,
        month=data.month,
        year=data.year,
        worked_days=data.worked_days,
        total_days=data.total_days,
        lop_days=data.lop_days,
        basic=basic,
        hra=hra,
        allowances=allowances,
        bonus=bonus,
        gross_salary=gross,
        pf=pf,
        professional_tax=pt,
        income_tax=it,
        total_deductions=total_ded,
        net_salary=net,
        generated_by=admin.id
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.get("/records", response_model=List[SalaryRecordOut])
def get_salary_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    employee_id: Optional[int] = None,
    year: Optional[int] = None
):
    q = db.query(SalaryRecord)
    if current_user.role == RoleEnum.employee:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not emp:
            return []
        q = q.filter(SalaryRecord.employee_id == emp.id)
    elif employee_id:
        q = q.filter(SalaryRecord.employee_id == employee_id)
    
    if year:
        q = q.filter(SalaryRecord.year == year)
    
    return q.order_by(SalaryRecord.year.desc(), SalaryRecord.month.desc()).all()

@router.get("/slip/{record_id}")
def download_salary_slip(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(SalaryRecord).filter(SalaryRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Salary record not found")

    # Authorization
    if current_user.role == RoleEnum.employee:
        emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not emp or emp.id != record.employee_id:
            raise HTTPException(status_code=403, detail="Not authorized")

    emp = db.query(Employee).filter(Employee.id == record.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    pdf_bytes = generate_salary_slip(emp, record)
    month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    filename = f"SalarySlip_{emp.employee_id}_{month_names.get(record.month,'')}{record.year}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
