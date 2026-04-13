"""FAQ CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.faq import FAQ
from app.models.user import User

router = APIRouter()


class FAQCreate(BaseModel):
    question: str = Field(..., min_length=5)
    answer: str = Field(..., min_length=10)
    category: str = "General"
    is_active: bool = True


class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


def faq_to_dict(f: FAQ) -> dict:
    return {
        "id": f.id,
        "question": f.question,
        "answer": f.answer,
        "category": f.category,
        "is_active": f.is_active,
        "usage_count": f.usage_count,
        "created_at": f.created_at.isoformat() if f.created_at else None,
        "updated_at": f.updated_at.isoformat() if f.updated_at else None,
    }


@router.get("/", response_model=List[dict])
async def list_faqs(
    category: Optional[str] = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    """List all FAQs (public for retrieval, filtered by category)."""
    q = db.query(FAQ)
    if category:
        q = q.filter(FAQ.category == category)
    if active_only:
        q = q.filter(FAQ.is_active == True)
    return [faq_to_dict(f) for f in q.order_by(FAQ.category, FAQ.id).all()]


@router.post("/", status_code=201)
async def create_faq(
    data: FAQCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    faq = FAQ(**data.model_dump(), created_by=admin.id)
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq_to_dict(faq)


@router.put("/{faq_id}")
async def update_faq(
    faq_id: int,
    data: FAQUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(faq, field, value)
    faq.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(faq)
    return faq_to_dict(faq)


@router.delete("/{faq_id}", status_code=204)
async def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    db.delete(faq)
    db.commit()


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    cats = db.query(FAQ.category).distinct().all()
    return [c[0] for c in cats]
