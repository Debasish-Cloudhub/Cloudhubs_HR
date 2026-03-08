from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from database.db import engine, Base
from routers import auth, employees, timesheets, payroll, holidays, documents, dashboard

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CloudHub HR Portal API",
    description="HR Management System for CloudHub",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(employees.router, prefix="/employees", tags=["Employees"])
app.include_router(timesheets.router, prefix="/timesheets", tags=["Timesheets"])
app.include_router(payroll.router, prefix="/payroll", tags=["Payroll"])
app.include_router(holidays.router, prefix="/holidays", tags=["Holidays"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"message": "CloudHub HR Portal API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}
