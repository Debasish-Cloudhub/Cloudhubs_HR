import sys
sys.path.insert(0, '.')
from database.db import SessionLocal, engine, Base
from models.models import User, Employee, Holiday, SalaryComponent, RoleEnum, EmploymentTypeEnum
from utils.auth import hash_password
from utils.employee_id import generate_employee_id
from datetime import date
Base.metadata.create_all(bind=engine)
db = SessionLocal()
if not db.query(User).filter(User.email == "admin@cloudhub.in").first():
    admin = User(email="admin@cloudhub.in", hashed_password=hash_password("Admin@123"), role=RoleEnum.admin)
    db.add(admin); db.flush()
    print("Admin created: admin@cloudhub.in / Admin@123")
else:
    print("Admin exists")
if not db.query(User).filter(User.email == "john.doe@cloudhub.in").first():
    eu = User(email="john.doe@cloudhub.in", hashed_password=hash_password("Employee@123"), role=RoleEnum.employee)
    db.add(eu); db.flush()
    eid = generate_employee_id(db, EmploymentTypeEnum.permanent)
    emp = Employee(user_id=eu.id, employee_id=eid, first_name="John", last_name="Doe", email="john.doe@cloudhub.in", phone="9876543210", designation="Software Engineer", department="Engineering", employment_type=EmploymentTypeEnum.permanent, date_of_joining=date(2023,1,15), bank_account="1234567890", bank_name="HDFC Bank", ifsc_code="HDFC0001234", pf_number="AP/HYD/123456", uan_number="100123456789")
    db.add(emp); db.flush()
    db.add(SalaryComponent(employee_id=emp.id, basic=50000, hra=20000, allowances=10000, bonus=5000, pf_deduction=6000, professional_tax=200, income_tax=2000, effective_from=date(2023,1,15)))
    print(f"Employee created: {eid}")
if not db.query(User).filter(User.email == "manager@cloudhub.in").first():
    mu = User(email="manager@cloudhub.in", hashed_password=hash_password("Manager@123"), role=RoleEnum.manager)
    db.add(mu); db.flush()
    mid = generate_employee_id(db, EmploymentTypeEnum.permanent)
    db.add(Employee(user_id=mu.id, employee_id=mid, first_name="Jane", last_name="Smith", email="manager@cloudhub.in", designation="Engineering Manager", department="Engineering", employment_type=EmploymentTypeEnum.permanent, date_of_joining=date(2022,6,1)))
    print(f"Manager created: {mid}")
for name, hdate in [("Republic Day",date(2025,1,26)),("Independence Day",date(2025,8,15)),("Gandhi Jayanti",date(2025,10,2)),("Diwali",date(2025,10,20)),("Christmas",date(2025,12,25))]:
    if not db.query(Holiday).filter(Holiday.date == hdate).first():
        db.add(Holiday(name=name, date=hdate))
db.commit(); db.close()
print("Seed complete!")