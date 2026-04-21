from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from models.models import User, Employee, RoleEnum, TerminationRecord, ResignationRecord, EmployeeStatusEnum, EmploymentTypeEnum
from schemas.schemas import EmployeeCreate, EmployeeOut
from utils.auth import get_current_user, require_admin, hash_password
from utils.employee_id import generate_employee_id
from pydantic import BaseModel
from datetime import date
import io

router = APIRouter()

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    employment_type: Optional[EmploymentTypeEnum] = None
    date_of_joining: Optional[date] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    pf_number: Optional[str] = None
    uan_number: Optional[str] = None

class PasswordResetRequest(BaseModel):
    new_password: str

class TerminateRequest(BaseModel):
    reason: str
    termination_date: date
    notes: Optional[str] = None

class ResignRequest(BaseModel):
    reason: Optional[str] = None
    notice_date: date
    last_working_date: Optional[date] = None

class AssignManagerRequest(BaseModel):
    manager_employee_id: int

class CreateAdminRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

def _generate_letter_pdf(title: str, body_lines: list, emp, footer_note: str = "") -> bytes:
    """Generate a professional letter PDF using ReportLab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
    from reportlab.lib.units import cm
    from datetime import datetime

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2.5*cm, rightMargin=2.5*cm)
    styles = getSampleStyleSheet()
    story = []

    # Header
    hdr_style = ParagraphStyle('H', fontName='Helvetica-Bold', fontSize=16,
                               textColor=colors.HexColor('#1e3a5f'), spaceAfter=4)
    sub_style = ParagraphStyle('S', fontName='Helvetica', fontSize=9,
                               textColor=colors.grey, spaceAfter=2)
    story.append(Paragraph("CloudHub Technologies Pvt. Ltd.", hdr_style))
    story.append(Paragraph("Hitech City, Hyderabad – 500081 | hr@cloudhub.in | +91-40-12345678", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1e3a5f'), spaceAfter=12))

    # Date + Ref
    today = datetime.now().strftime("%d %B %Y")
    ref = f"REF: CHIT/{emp.employee_id}/{datetime.now().strftime('%Y%m%d')}"
    meta = [[Paragraph(f"Date: {today}", styles['Normal']),
             Paragraph(ref, ParagraphStyle('R', fontName='Helvetica', fontSize=10, alignment=2))]]
    t = Table(meta, colWidths=[9*cm, 9*cm])
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # Title
    title_style = ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=13,
                                 textColor=colors.HexColor('#1e3a5f'), alignment=1, spaceAfter=16)
    story.append(Paragraph(title.upper(), title_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceAfter=12))

    # Salutation
    story.append(Paragraph(f"To Whomsoever It May Concern,", styles['Normal']))
    story.append(Spacer(1, 0.4*cm))

    # Body paragraphs
    body_style = ParagraphStyle('B', fontName='Helvetica', fontSize=11,
                                leading=18, spaceAfter=10)
    for line in body_lines:
        story.append(Paragraph(line, body_style))

    story.append(Spacer(1, 0.8*cm))

    # Signature block
    story.append(Paragraph("Yours sincerely,", styles['Normal']))
    story.append(Spacer(1, 1.2*cm))
    story.append(Paragraph("<b>HR Department</b>", styles['Normal']))
    story.append(Paragraph("CloudHub Technologies Pvt. Ltd.", styles['Normal']))
    story.append(Paragraph("Hitech City, Hyderabad – 500081", styles['Normal']))

    if footer_note:
        story.append(Spacer(1, 1*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
        note_style = ParagraphStyle('N', fontName='Helvetica-Oblique', fontSize=8,
                                    textColor=colors.grey, spaceBefore=6)
        story.append(Paragraph(footer_note, note_style))

    doc.build(story)
    buf.seek(0)
    return buf.read()


@router.post("/", response_model=EmployeeOut)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, hashed_password=hash_password(data.password), role=RoleEnum.employee)
    db.add(user); db.flush()
    emp_id = generate_employee_id(db, data.employment_type)
    emp = Employee(
        user_id=user.id, employee_id=emp_id,
        first_name=data.first_name, last_name=data.last_name, email=data.email,
        phone=data.phone, designation=data.designation, department=data.department,
        employment_type=data.employment_type, status=EmployeeStatusEnum.active,
        date_of_joining=data.date_of_joining, date_of_birth=data.date_of_birth,
        address=data.address, bank_account=data.bank_account, bank_name=data.bank_name,
        ifsc_code=data.ifsc_code, pf_number=data.pf_number, uan_number=data.uan_number
    )
    db.add(emp); db.commit(); db.refresh(emp); return emp

@router.get("/", response_model=List[EmployeeOut])
def list_employees(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(Employee).filter(Employee.is_active == True).all()

@router.get("/inactive", response_model=List[EmployeeOut])
def list_inactive_employees(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(Employee).filter(Employee.is_active == False).all()

@router.get("/me", response_model=EmployeeOut)
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp: raise HTTPException(status_code=404, detail="Profile not found")
    return emp

@router.get("/resignations/all")
def all_resignations(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    recs = db.query(ResignationRecord).order_by(ResignationRecord.created_at.desc()).all()
    result = []
    for r in recs:
        emp = db.query(Employee).filter(Employee.id == r.employee_id).first()
        result.append({
            "id": r.id, "employee_id": r.employee_id,
            "emp_name": (emp.first_name + " " + emp.last_name) if emp else "Unknown",
            "emp_code": emp.employee_id if emp else "",
            "designation": emp.designation if emp else "",
            "department": emp.department if emp else "",
            "date_of_joining": str(emp.date_of_joining) if emp and emp.date_of_joining else "",
            "reason": r.reason, "notice_date": str(r.notice_date),
            "last_working_date": str(r.last_working_date) if r.last_working_date else None,
            "status": r.status, "created_at": str(r.created_at)
        })
    return result

@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Not found")
    return emp

@router.put("/{employee_id}", response_model=EmployeeOut)
def edit_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(emp, field, value)
    db.commit(); db.refresh(emp); return emp

@router.post("/{employee_id}/reset-password")
def reset_password(employee_id: int, data: PasswordResetRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Admin resets an employee's password."""
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    user = db.query(User).filter(User.id == emp.user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User account not found")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": f"Password reset successfully for {emp.first_name} {emp.last_name}"}

@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    user = db.query(User).filter(User.id == emp.user_id).first()
    if user: user.is_active = False
    emp.is_active = False
    db.commit()
    return {"message": "Employee deleted", "employee_id": emp.employee_id}

@router.post("/{employee_id}/reinstate")
def reinstate_employee(employee_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    if emp.is_active: raise HTTPException(status_code=400, detail="Employee is already active")
    emp.is_active = True
    emp.status = EmployeeStatusEnum.active
    user = db.query(User).filter(User.id == emp.user_id).first()
    if user: user.is_active = True
    db.commit()
    return {"message": "Employee reinstated successfully", "employee_id": emp.employee_id}

@router.post("/{employee_id}/terminate")
def terminate_employee(employee_id: int, data: TerminateRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    emp.status = EmployeeStatusEnum.terminated
    emp.is_active = False
    user = db.query(User).filter(User.id == emp.user_id).first()
    if user: user.is_active = False
    rec = TerminationRecord(employee_id=emp.id, reason=data.reason,
                            termination_date=data.termination_date,
                            terminated_by=admin.id, notes=data.notes)
    db.add(rec); db.commit()
    return {"message": "Employee terminated", "employee_id": emp.employee_id}

@router.post("/{employee_id}/assign-manager")
def assign_manager(employee_id: int, data: AssignManagerRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    mgr = db.query(Employee).filter(Employee.id == data.manager_employee_id).first()
    if not mgr: raise HTTPException(status_code=404, detail="Manager not found")
    emp.manager_id = mgr.id
    db.commit()
    return {"message": "Manager assigned", "manager": mgr.first_name + " " + mgr.last_name}

@router.post("/admin/create")
def create_admin(data: CreateAdminRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    new_admin = User(email=data.email, hashed_password=hash_password(data.password), role=RoleEnum.admin)
    db.add(new_admin); db.flush()
    emp_id = generate_employee_id(db, EmploymentTypeEnum.permanent)
    emp = Employee(user_id=new_admin.id, employee_id=emp_id,
                   first_name=data.first_name, last_name=data.last_name,
                   email=data.email, employment_type=EmploymentTypeEnum.permanent,
                   status=EmployeeStatusEnum.active)
    db.add(emp); db.commit()
    return {"message": "Admin created", "email": data.email}

@router.post("/me/resign")
def apply_resignation(data: ResignRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    rec = ResignationRecord(employee_id=emp.id, reason=data.reason,
                            notice_date=data.notice_date,
                            last_working_date=data.last_working_date)
    db.add(rec); db.commit(); db.refresh(rec)
    return {"message": "Resignation submitted", "id": rec.id}

@router.get("/{employee_id}/letter/employment")
def employment_letter(employee_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Generate Employment Verification Letter (Feature 6)."""
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    from datetime import datetime
    doj = str(emp.date_of_joining) if emp.date_of_joining else "N/A"
    body = [
        f"This is to certify that <b>{emp.first_name} {emp.last_name}</b> (Employee ID: "
        f"<b>{emp.employee_id}</b>) is currently employed with CloudHub Technologies Pvt. Ltd. "
        f"as a <b>{emp.designation or 'Employee'}</b> in the <b>{emp.department or 'CloudHub'}</b> department.",
        f"The employee has been associated with our organization since <b>{doj}</b> and is "
        f"a permanent employee on our rolls as of the date of this letter.",
        "This letter is issued at the request of the employee for identification, bank account "
        "opening, address proof, or any other bonafide purpose.",
        "We wish the employee all the best in their endeavours."
    ]
    pdf = _generate_letter_pdf("Employment Verification Letter", body, emp,
                               "This is a computer-generated letter and does not require a physical signature.")
    fname = f"Employment_Letter_{emp.employee_id}.pdf"
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})

@router.get("/resignations/{resignation_id}/letter")
def relieving_letter(resignation_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Generate Relieving / Experience Letter (Feature 5)."""
    rec = db.query(ResignationRecord).filter(ResignationRecord.id == resignation_id).first()
    if not rec: raise HTTPException(status_code=404, detail="Resignation record not found")
    emp = db.query(Employee).filter(Employee.id == rec.employee_id).first()
    if not emp: raise HTTPException(status_code=404, detail="Employee not found")
    doj = str(emp.date_of_joining) if emp.date_of_joining else "N/A"
    lwd = str(rec.last_working_date) if rec.last_working_date else "N/A"
    body = [
        f"This is to certify that <b>{emp.first_name} {emp.last_name}</b> (Employee ID: "
        f"<b>{emp.employee_id}</b>) was employed with CloudHub Technologies Pvt. Ltd. as "
        f"<b>{emp.designation or 'Employee'}</b> in the <b>{emp.department or 'CloudHub'}</b> department "
        f"from <b>{doj}</b> to <b>{lwd}</b>.",
        "During the tenure of employment, the employee demonstrated professionalism, "
        "dedication, and commitment to their responsibilities. They have discharged "
        "their duties diligently and to our satisfaction.",
        "The employee is relieved from services with effect from the last working date "
        "mentioned above, and there are no dues pending against them as on the date of this letter.",
        "We wish them success in all future endeavours."
    ]
    pdf = _generate_letter_pdf("Relieving & Experience Letter", body, emp,
                               "This letter is issued upon request at the time of separation from services.")
    fname = f"Relieving_Letter_{emp.employee_id}.pdf"
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})
