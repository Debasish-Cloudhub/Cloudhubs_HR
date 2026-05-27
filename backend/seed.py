import sys, os
sys.path.insert(0, '.')
from database.db import SessionLocal, engine, Base
from models.models import User, Employee, Holiday, SalaryComponent, LeaveConfig, LeaveBalance, LeaveTypeEnum, RoleEnum, EmploymentTypeEnum, EmployeeStatusEnum
from utils.auth import hash_password
from utils.employee_id import generate_employee_id
from datetime import date
from sqlalchemy import text

# Create all tables (new ones)
Base.metadata.create_all(bind=engine)

# ─── MIGRATION: add missing columns to existing tables ───
with engine.connect() as conn:
    # Add status column to employees if missing
    try:
        conn.execute(text("ALTER TABLE employees ADD COLUMN status VARCHAR DEFAULT 'active'"))
        conn.commit()
        print("Migration: added employees.status")
    except Exception as e:
        if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
            print("Migration: employees.status already exists")
        else:
            print("Migration warning (status):", e)
            conn.rollback()

    # Add manager_id column to employees if missing
    try:
        conn.execute(text("ALTER TABLE employees ADD COLUMN manager_id INTEGER REFERENCES employees(id)"))
        conn.commit()
        print("Migration: added employees.manager_id")
    except Exception as e:
        if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
            print("Migration: employees.manager_id already exists")
        else:
            print("Migration warning (manager_id):", e)
            conn.rollback()

    # Update any NULL status values to 'active'
    try:
        conn.execute(text("UPDATE employees SET status = 'active' WHERE status IS NULL"))
        conn.commit()
        print("Migration: updated NULL status values")
    except Exception as e:
        print("Migration warning (update status):", e)
        conn.rollback()

print("Migrations complete")

def _safe_add_feature_columns():
    dialect = engine.dialect.name
    if dialect == "postgresql":
        type_map = {
            "float": "DOUBLE PRECISION",
            "text": "TEXT",
            "int": "INTEGER",
            "datetime": "TIMESTAMP WITH TIME ZONE",
        }
        def add(table, col, typ):
            return f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {type_map[typ]}"
        enum_statements = [
            "ALTER TYPE appraisalstatusenum ADD VALUE IF NOT EXISTS 'pending_hr_approval'",
            "ALTER TYPE appraisalstatusenum ADD VALUE IF NOT EXISTS 'approved'",
            "ALTER TYPE appraisalstatusenum ADD VALUE IF NOT EXISTS 'rejected'",
        ]
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            for stmt in enum_statements:
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    print("Migration warning (appraisal enum):", e)
    else:
        type_map = {"float": "FLOAT", "text": "TEXT", "int": "INTEGER", "datetime": "DATETIME"}
        def add(table, col, typ):
            return f"ALTER TABLE {table} ADD COLUMN {col} {type_map[typ]}"

    feature_columns = [
        ("salary_components", "lta", "float"), ("salary_components", "extra_earnings", "text"),
        ("salary_components", "extra_deductions", "text"), ("salary_records", "lta", "float"),
        ("salary_records", "misc_deductions", "float"), ("salary_records", "extra_earnings", "text"),
        ("salary_records", "extra_deductions", "text"), ("salary_records", "deduction_breakdown", "text"),
        ("appraisals", "assigned_manager_id", "int"), ("appraisals", "additional_reviewer_ids", "text"),
        ("appraisals", "appraisal_year", "int"), ("appraisals", "manager_feedback", "text"),
        ("appraisals", "additional_reviewer_feedback", "text"), ("appraisals", "salary_hike_percent", "float"),
        ("appraisals", "final_status", "text"), ("appraisals", "approved_by", "int"),
        ("appraisals", "approved_at", "datetime"),
    ]
    with engine.connect() as conn:
        for table, col, typ in feature_columns:
            try:
                conn.execute(text(add(table, col, typ)))
                conn.commit()
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    conn.rollback()
                else:
                    print(f"Migration warning ({table}.{col}):", e)
                    conn.rollback()

_safe_add_feature_columns()
print("Feature migrations complete")

# ─── SEED DATA ───
db = SessionLocal()

if not db.query(User).filter(User.email == "admin@cloudhub.in").first():
    admin = User(email="admin@cloudhub.in", hashed_password=hash_password("Admin@123"), role=RoleEnum.admin)
    db.add(admin); db.flush()
    print("Admin created")
else:
    print("Admin exists")

if not db.query(User).filter(User.email == "john.doe@cloudhub.in").first():
    eu = User(email="john.doe@cloudhub.in", hashed_password=hash_password("Employee@123"), role=RoleEnum.employee)
    db.add(eu); db.flush()
    eid = generate_employee_id(db, EmploymentTypeEnum.permanent)
    emp = Employee(
        user_id=eu.id, employee_id=eid, first_name="John", last_name="Doe",
        email="john.doe@cloudhub.in", phone="9876543210", designation="Software Engineer",
        department="Engineering", employment_type=EmploymentTypeEnum.permanent,
        status=EmployeeStatusEnum.active, date_of_joining=date(2023,1,15),
        bank_account="1234567890", bank_name="HDFC Bank", ifsc_code="HDFC0001234",
        pf_number="AP/HYD/123456", uan_number="100123456789"
    )
    db.add(emp); db.flush()
    db.add(SalaryComponent(
        employee_id=emp.id, basic=50000, hra=20000, allowances=10000, bonus=5000,
        pf_deduction=6000, professional_tax=200, income_tax=2000, effective_from=date(2023,1,15)
    ))
    for lt, days in [(LeaveTypeEnum.paid,12),(LeaveTypeEnum.sick,8),(LeaveTypeEnum.earned,15),(LeaveTypeEnum.sabbatical,5),(LeaveTypeEnum.lop,0)]:
        db.add(LeaveBalance(employee_id=emp.id, leave_type=lt, total_days=days, used_days=0, remaining_days=days, year=date.today().year))
    print("Employee created:", eid)
else:
    print("Employee exists")

if not db.query(User).filter(User.email == "manager@cloudhub.in").first():
    mu = User(email="manager@cloudhub.in", hashed_password=hash_password("Manager@123"), role=RoleEnum.manager)
    db.add(mu); db.flush()
    mid = generate_employee_id(db, EmploymentTypeEnum.permanent)
    db.add(Employee(
        user_id=mu.id, employee_id=mid, first_name="Jane", last_name="Smith",
        email="manager@cloudhub.in", designation="Engineering Manager",
        department="Engineering", employment_type=EmploymentTypeEnum.permanent,
        status=EmployeeStatusEnum.active, date_of_joining=date(2022,6,1)
    ))
    print("Manager created:", mid)
else:
    print("Manager exists")

# Leave config
for lt, days, cf, desc in [
    (LeaveTypeEnum.paid, 12, False, "Paid Annual Leave"),
    (LeaveTypeEnum.sick, 8, False, "Sick Leave"),
    (LeaveTypeEnum.earned, 15, True, "Earned Leave"),
    (LeaveTypeEnum.sabbatical, 5, False, "Sabbatical Leave"),
    (LeaveTypeEnum.lop, 0, False, "Leave Without Pay"),
]:
    if not db.query(LeaveConfig).filter(LeaveConfig.leave_type == lt).first():
        db.add(LeaveConfig(leave_type=lt, days_per_year=days, carry_forward=cf, description=desc))

# Holidays
for name, hdate in [
    ("Republic Day", date(2025,1,26)), ("Independence Day", date(2025,8,15)),
    ("Gandhi Jayanti", date(2025,10,2)), ("Diwali", date(2025,10,20)),
    ("Christmas", date(2025,12,25)),
]:
    if not db.query(Holiday).filter(Holiday.date == hdate).first():
        db.add(Holiday(name=name, date=hdate))

db.commit(); db.close()
print("Seed v2 complete!")
