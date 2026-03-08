"""Seed initial data: admin user + sample employees + holidays"""
import sys
sys.path.insert(0, '.')

from database.db import SessionLocal, engine, Base
from models.models import User, Employee, Holiday, SalaryComponent, RoleEnum, EmploymentTypeEnum
from utils.auth import hash_password
from utils.employee_id import generate_employee_id
from datetime import date

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Admin user
existing_admin = db.query(User).filter(User.email == "admin@cloudhub.in").first()
if not existing_admin:
    admin_user = User(
        email="admin@cloudhub.in",
        hashed_password=hash_password("Admin@123"),
        role=RoleEnum.admin
    )
    db.add(admin_user)
    db.flush()
    print(f"✅ Admin created: admin@cloudhub.in / Admin@123")
else:
    admin_user = existing_admin
    print("ℹ️  Admin already exists")

# Sample employee
existing_emp_user = db.query(User).filter(User.email == "john.doe@cloudhub.in").first()
if not existing_emp_user:
    emp_user = User(
        email="john.doe@cloudhub.in",
        hashed_password=hash_password("Employee@123"),
        role=RoleEnum.employee
    )
    db.add(emp_user)
    db.flush()

    emp_id = generate_employee_id(db, EmploymentTypeEnum.permanent)
    employee = Employee(
        user_id=emp_user.id,
        employee_id=emp_id,
        full_name="John Doe",
        email="john.doe@cloudhub.in",
        phone="+91-9876543210",
        department="Engineering",
        designation="Software Engineer",
        location="Hyderabad",
        date_of_joining=date(2023, 1, 15),
        employment_type=EmploymentTypeEnum.permanent,
        bank_name="HDFC Bank",
        bank_account="1234567890",
        ifsc="HDFC0001234",
        pf_number="AP/HYD/12345/001",
        uan="100123456789",
        pan="ABCDE1234F"
    )
    db.add(employee)
    db.flush()

    salary = SalaryComponent(
        employee_id=employee.id,
        basic=40000,
        hra=16000,
        allowances=5000,
        bonus=0,
        pf=1800,
        professional_tax=200,
        income_tax=0,
        effective_from=date(2023, 1, 15)
    )
    db.add(salary)
    print(f"✅ Employee created: john.doe@cloudhub.in / Employee@123 (ID: {emp_id})")
else:
    print("ℹ️  Sample employee already exists")

# Sample manager
existing_mgr = db.query(User).filter(User.email == "manager@cloudhub.in").first()
if not existing_mgr:
    mgr_user = User(
        email="manager@cloudhub.in",
        hashed_password=hash_password("Manager@123"),
        role=RoleEnum.manager
    )
    db.add(mgr_user)
    db.flush()

    mgr_id = generate_employee_id(db, EmploymentTypeEnum.permanent)
    manager = Employee(
        user_id=mgr_user.id,
        employee_id=mgr_id,
        full_name="Sarah Manager",
        email="manager@cloudhub.in",
        phone="+91-9876543211",
        department="Engineering",
        designation="Engineering Manager",
        location="Hyderabad",
        date_of_joining=date(2022, 6, 1),
        employment_type=EmploymentTypeEnum.permanent,
    )
    db.add(manager)
    print(f"✅ Manager created: manager@cloudhub.in / Manager@123 (ID: {mgr_id})")
else:
    print("ℹ️  Sample manager already exists")

# Holidays 2025
holidays_2025 = [
    ("New Year's Day", date(2025, 1, 1), "New Year Celebration"),
    ("Republic Day", date(2025, 1, 26), "National Holiday"),
    ("Holi", date(2025, 3, 14), "Festival of Colors"),
    ("Good Friday", date(2025, 4, 18), "Christian Holiday"),
    ("Eid ul-Fitr", date(2025, 3, 31), "Muslim Festival"),
    ("Independence Day", date(2025, 8, 15), "National Holiday"),
    ("Gandhi Jayanti", date(2025, 10, 2), "National Holiday"),
    ("Dussehra", date(2025, 10, 2), "Hindu Festival"),
    ("Diwali", date(2025, 10, 20), "Festival of Lights"),
    ("Christmas", date(2025, 12, 25), "Christian Holiday"),
]

existing_holidays = db.query(Holiday).count()
if existing_holidays == 0:
    for name, d, desc in holidays_2025:
        db.add(Holiday(name=name, date=d, description=desc))
    print(f"✅ {len(holidays_2025)} holidays added for 2025")

db.commit()
db.close()
print("\n🎉 Database seeded successfully!")
print("\nCredentials:")
print("  Admin:    admin@cloudhub.in    / Admin@123")
print("  Employee: john.doe@cloudhub.in / Employee@123")
print("  Manager:  manager@cloudhub.in  / Manager@123")
