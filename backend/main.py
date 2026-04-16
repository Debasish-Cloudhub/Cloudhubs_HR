from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from database.db import engine, Base
from routers import auth, employees, timesheets, payroll, holidays, documents, dashboard, leaves
Base.metadata.create_all(bind=engine)
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
@app.get("/api")
def root(): return {"message": "CloudHub HR Portal API v2.0", "status": "running"}
@app.get("/health")
def health(): return {"status": "healthy"}
@app.get("/")
def serve_ui():
    ui_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(ui_path):
        return FileResponse(ui_path, media_type="text/html")
    return {"message": "CloudHub HR Portal API v2.0", "docs": "/docs"}
