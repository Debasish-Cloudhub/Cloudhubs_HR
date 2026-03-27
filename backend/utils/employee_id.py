from sqlalchemy.orm import Session
from models.models import Employee, EmploymentTypeEnum
PREFIX_MAP = {EmploymentTypeEnum.permanent: "CH-EMP", EmploymentTypeEnum.contractor: "CH-CON", EmploymentTypeEnum.intern: "CH-INT", EmploymentTypeEnum.consultant: "CH-CON"}
def generate_employee_id(db, employment_type):
    prefix = PREFIX_MAP.get(employment_type, "CH-EMP")
    existing = db.query(Employee).filter(Employee.employee_id.like(f"{prefix}-%")).order_by(Employee.id.desc()).first()
    if existing:
        try: next_num = int(existing.employee_id.split("-")[-1]) + 1
        except: next_num = 1
    else: next_num = 1
    return f"{prefix}-{next_num:04d}"