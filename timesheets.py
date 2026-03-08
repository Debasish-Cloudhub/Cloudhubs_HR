from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.models import User, Employee, RoleEnum
from schemas.schemas import LoginRequest, TokenResponse
from utils.auth import verify_password, create_access_token, hash_password

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is deactivated")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role.value,
        employee_id=employee.employee_id if employee else None,
        user_id=user.id,
        name=employee.full_name if employee else user.email
    )

@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(__import__('utils.auth', fromlist=['get_current_user']).get_current_user)
):
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(new_password)
    db.commit()
    return {"message": "Password changed successfully"}
