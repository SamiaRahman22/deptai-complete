"""Procedure CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.procedure import Procedure
from app.models.user import User

router = APIRouter()


class ProcedureCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: Optional[str] = None
    category: str = "General"
    steps: List[str] = Field(..., min_items=1)
    is_active: bool = True


class ProcedureUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    steps: Optional[List[str]] = None
    is_active: Optional[bool] = None


def proc_to_dict(p: Procedure) -> dict:
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "category": p.category,
        "steps": p.steps,
        "is_active": p.is_active,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


@router.get("/", response_model=List[dict])
async def list_procedures(
    category: Optional[str] = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    q = db.query(Procedure)
    if category:
        q = q.filter(Procedure.category == category)
    if active_only:
        q = q.filter(Procedure.is_active == True)
    return [proc_to_dict(p) for p in q.order_by(Procedure.category, Procedure.title).all()]


@router.post("/", status_code=201)
async def create_procedure(
    data: ProcedureCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    proc = Procedure(**data.model_dump(), created_by=admin.id)
    db.add(proc)
    db.commit()
    db.refresh(proc)
    return proc_to_dict(proc)


@router.put("/{proc_id}")
async def update_procedure(
    proc_id: int,
    data: ProcedureUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    proc = db.query(Procedure).filter(Procedure.id == proc_id).first()
    if not proc:
        raise HTTPException(status_code=404, detail="Procedure not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(proc, field, value)
    proc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(proc)
    return proc_to_dict(proc)


@router.delete("/{proc_id}", status_code=204)
async def delete_procedure(
    proc_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    proc = db.query(Procedure).filter(Procedure.id == proc_id).first()
    if not proc:
        raise HTTPException(status_code=404, detail="Procedure not found")
    db.delete(proc)
    db.commit()
