from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os, shutil, uuid
from database.db import get_db
from models.models import User, Document
from schemas.schemas import DocumentOut
from utils.auth import get_current_user, require_admin

router = APIRouter()
UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=DocumentOut)
async def upload_document(
    title: str = Form(...),
    description: str = Form(None),
    category: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, unique_name)
    
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    doc = Document(
        title=title,
        description=description,
        category=category,
        filename=file.filename,
        filepath=filepath,
        uploaded_by=admin.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.get("/", response_model=List[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category: Optional[str] = None
):
    q = db.query(Document)
    if category:
        q = q.filter(Document.category == category)
    return q.order_by(Document.created_at.desc()).all()

@router.get("/{doc_id}/download")
def download_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not os.path.exists(doc.filepath):
        raise HTTPException(status_code=404, detail="File not found on server")
    return FileResponse(doc.filepath, filename=doc.filename)

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if os.path.exists(doc.filepath):
        os.remove(doc.filepath)
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}
