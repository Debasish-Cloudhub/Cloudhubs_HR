[README.md](https://github.com/user-attachments/files/25822082/README.md)
# CloudHub HR Portal

A complete, production-ready HR Management System for CloudHub built with FastAPI, Next.js, PostgreSQL, and Docker.

---

## 🌟 Features

| Module | Description |
|---|---|
| **Employee Onboarding** | Add employees with auto-generated unique IDs |
| **Employee Types** | Permanent (CH-EMP), Contractor (CH-CON), Intern (CH-INT) |
| **Timesheet Management** | Submit, approve, reject daily timesheets |
| **Salary Processing** | Define components, generate salary with calculations |
| **Salary Slip PDF** | Download professional PDF payslips |
| **Holiday Calendar** | Admin defines, employees view |
| **HR Documents** | Upload and share policies/handbooks |
| **Role-Based Access** | Admin, Manager, Employee roles |
| **JWT Authentication** | Secure token-based auth |

---

## 🔐 Demo Credentials

| Role | Email | Password |
|---|---|---|
| **HR Admin** | admin@cloudhub.in | Admin@123 |
| **Employee** | john.doe@cloudhub.in | Employee@123 |
| **Manager** | manager@cloudhub.in | Manager@123 |

---

## 🚀 Quick Start (Docker — Recommended)

### Prerequisites
- Docker & Docker Compose installed

### Steps

```bash
# 1. Clone or extract the project
cd cloudhub-hr

# 2. Start all services
docker-compose -f docker/docker-compose.yml up --build

# 3. Wait for services to start (~30-60 seconds)
# Database seeds automatically with demo data

# 4. Open the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 🛠 Local Development Setup

### Backend

```bash
# Prerequisites: Python 3.11+, PostgreSQL running

cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://cloudhub:cloudhub123@localhost:5432/cloudhub_hr"
export SECRET_KEY="your-secret-key"

# Create database
createdb cloudhub_hr  # or use psql

# Seed demo data
python seed.py

# Start server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
# Prerequisites: Node.js 18+

cd frontend

# Install dependencies
npm install

# Set env variable
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

---

## 📁 Project Structure

```
cloudhub-hr/
├── backend/
│   ├── main.py                  # FastAPI app entry
│   ├── requirements.txt
│   ├── seed.py                  # DB seed script
│   ├── Dockerfile
│   ├── database/
│   │   └── db.py               # SQLAlchemy setup
│   ├── models/
│   │   └── models.py           # All ORM models
│   ├── schemas/
│   │   └── schemas.py          # Pydantic schemas
│   ├── routers/
│   │   ├── auth.py             # Login endpoint
│   │   ├── employees.py        # Employee CRUD
│   │   ├── timesheets.py       # Timesheet management
│   │   ├── payroll.py          # Salary & payslips
│   │   ├── holidays.py         # Holiday calendar
│   │   ├── documents.py        # HR documents
│   │   └── dashboard.py        # Dashboard stats
│   └── utils/
│       ├── auth.py             # JWT & password utils
│       ├── employee_id.py      # ID generation
│       └── pdf_generator.py    # ReportLab salary slip
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index.tsx       # Redirect
│   │   │   ├── login.tsx       # Login page
│   │   │   ├── admin/
│   │   │   │   ├── dashboard.tsx
│   │   │   │   ├── employees.tsx
│   │   │   │   ├── onboarding.tsx
│   │   │   │   ├── timesheets.tsx
│   │   │   │   ├── payroll.tsx
│   │   │   │   ├── holidays.tsx
│   │   │   │   └── documents.tsx
│   │   │   └── employee/
│   │   │       ├── dashboard.tsx
│   │   │       ├── timesheets.tsx
│   │   │       ├── payslips.tsx
│   │   │       ├── holidays.tsx
│   │   │       ├── documents.tsx
│   │   │       └── profile.tsx
│   │   ├── components/
│   │   │   └── common/
│   │   │       ├── Layout.tsx
│   │   │       └── AuthContext.tsx
│   │   ├── services/
│   │   │   └── api.ts          # Axios API calls
│   │   └── styles/
│   │       └── globals.css
│   ├── package.json
│   ├── tailwind.config.js
│   ├── next.config.js
│   └── Dockerfile
│
└── docker/
    └── docker-compose.yml
```

---

## 🗄 Database Schema

### Tables
- **users** — Auth credentials, role (admin/employee/manager)
- **employees** — Employee details, IDs, bank info
- **timesheets** — Daily time logs with approval workflow
- **salary_components** — Salary structure per employee
- **salary_records** — Generated payslips
- **holidays** — Company holiday calendar
- **documents** — HR policy documents
- **projects** — Project reference (extensible)

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | /auth/login | Login |
| GET | /employees | List employees (admin) |
| POST | /employees | Create employee (admin) |
| GET | /employees/me | My profile |
| POST | /timesheets/submit | Submit timesheet |
| GET | /timesheets | List timesheets |
| PUT | /timesheets/{id}/approve | Approve/reject timesheet |
| POST | /payroll/components | Set salary structure |
| POST | /payroll/generate | Generate payslip |
| GET | /payroll/slip/{id} | Download PDF payslip |
| GET | /holidays | List holidays |
| POST | /holidays | Add holiday (admin) |
| GET | /documents | List documents |
| POST | /documents | Upload document (admin) |

**Full API docs:** http://localhost:8000/docs

---

## 📄 Salary Slip

The salary slip PDF includes:
- Company header (CloudHub, Hyderabad address)
- Employee details (ID, name, designation, bank, PF, UAN)
- Earnings table (Basic, HRA, Allowances, Bonus)
- Deductions table (PF, Professional Tax, Income Tax)
- Net pay summary
- Auto-generated timestamp

---

## 🔒 Security

- Passwords hashed with bcrypt
- JWT tokens (8-hour expiry)
- Role-based route guards
- Employees cannot access other employee data
- Admin endpoints protected

---

## 🏗 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 15 |
| Authentication | JWT (python-jose) |
| PDF | ReportLab |
| Frontend | Next.js 14, React 18 |
| Styling | TailwindCSS |
| HTTP Client | Axios |
| Deployment | Docker + Docker Compose |
