from sqlalchemy.orm import Session
from models.models import Employee, EmploymentTypeEnum

PREFIX_MAP = {
    EmploymentTypeEnum.permanent: "CH-EMP",
    EmploymentTypeEnum.contractor: "CH-CON",
    EmploymentTypeEnum.intern: "CH-INT",
    EmploymentTypeEnum.consultant: "CH-CON",
}

def generate_employee_id(db: Session, employment_type: EmploymentTypeEnum) -> str:
    prefix = PREFIX_MAP.get(employment_type, "CH-EMP")
    # Find last employee of this type
    existing = db.query(Employee).filter(
        Employee.employee_id.like(f"{prefix}-%")
    ).order_by(Employee.id.desc()).first()
    
    if existing:
        try:
            last_num = int(existing.employee_id.split("-")[-1])
            next_num = last_num + 1
        except:
            next_num = 1
    else:
        next_num = 1
    
    return f"{prefix}-{next_num:04d}"
