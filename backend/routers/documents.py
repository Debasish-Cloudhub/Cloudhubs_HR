from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os, shutil, uuid
from database.db import get_db
from models.models import User, Document
from schemas.schemas import DocumentOut
from utils.auth import get_current_user, require_admin
router = APIRouter()
UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)
@router.post("/", response_model=DocumentOut)
def upload_document(title: str = Form(...), description: str = Form(None), is_public: bool = Form(True), file: UploadFile = File(...), db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as f: shutil.copyfileobj(file.file, f)
    doc = Document(title=title, description=description, file_path=file_path, file_name=file.filename, uploaded_by=admin.id, is_public=is_public)
    db.add(doc); db.commit(); db.refresh(doc); return doc
@router.get("/", response_model=List[DocumentOut])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Document).filter(Document.is_public == True).order_by(Document.created_at.desc()).all()
@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc: raise HTTPException(status_code=404, detail="Not found")
    if os.path.exists(doc.file_path): os.remove(doc.file_path)
    db.delete(doc); db.commit(); return {"message": "Deleted"}