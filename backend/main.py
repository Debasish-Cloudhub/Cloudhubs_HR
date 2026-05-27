from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from database.db import engine, Base
from sqlalchemy import text
from routers import auth, employees, timesheets, payroll, holidays, documents, dashboard, leaves, misc_deductions, appraisals

Base.metadata.create_all(bind=engine)

def apply_additive_schema_updates():
    """Keep existing deployments compatible with new optional HR/payroll fields."""
    dialect = engine.dialect.name
    statements = []
    if dialect == "postgresql":
        statements.extend([
            "ALTER TYPE appraisalstatusenum ADD VALUE IF NOT EXISTS 'pending_hr_approval'",
            "ALTER TYPE appraisalstatusenum ADD VALUE IF NOT EXISTS 'approved'",
            "ALTER TYPE appraisalstatusenum ADD VALUE IF NOT EXISTS 'rejected'",
        ])
        column_type = {
            "float": "DOUBLE PRECISION",
            "text": "TEXT",
            "int": "INTEGER",
            "datetime": "TIMESTAMP WITH TIME ZONE",
        }
        add = lambda table, col, typ: f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {column_type[typ]}"
    else:
        column_type = {"float": "FLOAT", "text": "TEXT", "int": "INTEGER", "datetime": "DATETIME"}
        add = lambda table, col, typ: f"ALTER TABLE {table} ADD COLUMN {col} {column_type[typ]}"
    new_columns = [
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
    statements.extend(add(table, col, typ) for table, col, typ in new_columns)
    with engine.begin() as conn:
        for stmt in statements:
            try:
                conn.execute(text(stmt))
            except Exception:
                if dialect == "postgresql":
                    raise

apply_additive_schema_updates()
app = FastAPI(title="CloudHub HR Portal API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(employees.router, prefix="/employees", tags=["Employees"])
app.include_router(timesheets.router, prefix="/timesheets", tags=["Timesheets"])
app.include_router(payroll.router, prefix="/payroll", tags=["Payroll"])
app.include_router(holidays.router, prefix="/holidays", tags=["Holidays & Leaves"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(leaves.router, prefix="/leaves", tags=["Leave Management"])
app.include_router(misc_deductions.router, prefix="/misc-deductions", tags=["Misc Deductions"])
app.include_router(appraisals.router, prefix="/appraisals", tags=["Appraisals"])

@app.get("/api")
def root(): 
    return {"message": "CloudHub HR Portal API v2.0", "status": "running"}

@app.get("/health")
def health(): 
    return {"status": "healthy"}

@app.get("/")
def serve_ui():
    ui_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(ui_path):
        with open(ui_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return Response(content=html_content, media_type="text/html; charset=utf-8")
    return {"message": "CloudHub HR Portal API v2.0", "docs": "/docs"}
