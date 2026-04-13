"""Admin-only endpoints: dashboard stats, query logs, user management."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_admin, hash_password
from app.models.user import User
from app.models.query_log import QueryLog
from app.models.faq import FAQ
from app.models.document import Document
from app.models.procedure import Procedure

router = APIRouter()


@router.get("/dashboard")
async def dashboard_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Comprehensive dashboard statistics."""
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    total_queries = db.query(QueryLog).filter(QueryLog.created_at >= thirty_days_ago).count()
    resolved = db.query(QueryLog).filter(
        QueryLog.created_at >= thirty_days_ago, QueryLog.status == "resolved"
    ).count()
    rejected = db.query(QueryLog).filter(
        QueryLog.created_at >= thirty_days_ago, QueryLog.is_in_domain == False
    ).count()
    active_students = db.query(User).filter(User.role == "student", User.is_active == True).count()
    faq_count = db.query(FAQ).filter(FAQ.is_active == True).count()
    doc_count = db.query(Document).filter(Document.status == "indexed").count()
    proc_count = db.query(Procedure).filter(Procedure.is_active == True).count()

    avg_response = db.query(func.avg(QueryLog.response_time_ms)).filter(
        QueryLog.created_at >= thirty_days_ago,
        QueryLog.response_time_ms.isnot(None)
    ).scalar() or 0

    # Recent activity
    recent_logs = db.query(QueryLog).order_by(desc(QueryLog.created_at)).limit(10).all()

    return {
        "stats": {
            "total_queries_30d": total_queries,
            "resolved": resolved,
            "rejected_ood": rejected,
            "resolution_rate": round(resolved / total_queries * 100, 1) if total_queries else 0,
            "active_students": active_students,
            "faq_count": faq_count,
            "document_count": doc_count,
            "procedure_count": proc_count,
            "avg_response_ms": round(avg_response),
        },
        "recent_activity": [
            {
                "id": l.id,
                "query": l.query[:100],
                "status": l.status,
                "is_in_domain": l.is_in_domain,
                "response_time_ms": l.response_time_ms,
                "created_at": l.created_at.isoformat(),
            }
            for l in recent_logs
        ],
    }


@router.get("/logs")
async def query_logs(
    page: int = 1,
    limit: int = 50,
    status: Optional[str] = None,
    in_domain: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Paginated query logs with filtering."""
    q = db.query(QueryLog).order_by(desc(QueryLog.created_at))

    if status:
        q = q.filter(QueryLog.status == status)
    if in_domain is not None:
        q = q.filter(QueryLog.is_in_domain == in_domain)
    if search:
        q = q.filter(QueryLog.query.ilike(f"%{search}%"))

    total = q.count()
    logs = q.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "logs": [
            {
                "id": l.id,
                "user_id": l.user_id,
                "query": l.query,
                "response": l.response[:500] if l.response else None,
                "is_in_domain": l.is_in_domain,
                "domain_score": l.domain_score,
                "retrieval_method": l.retrieval_method,
                "sources_used": l.sources_used,
                "response_time_ms": l.response_time_ms,
                "status": l.status,
                "created_at": l.created_at.isoformat(),
            }
            for l in logs
        ],
    }


@router.get("/users")
async def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    users = db.query(User).filter(User.role == "student").order_by(desc(User.created_at)).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "student_id": u.student_id,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_login": u.last_login.isoformat() if u.last_login else None,
            "query_count": u.query_logs.count(),
        }
        for u in users
    ]


@router.post("/users/{user_id}/toggle")
async def toggle_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    db.commit()
    return {"id": user.id, "is_active": user.is_active}


@router.post("/seed")
async def seed_database(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Seed initial FAQs and procedures (idempotent)."""
    if db.query(FAQ).count() > 0:
        return {"message": "Already seeded"}

    faqs = [
        FAQ(question="What is the minimum CGPA requirement to graduate?",
            answer="Students must maintain a minimum CGPA of 2.5 to be eligible for graduation. Students with CGPA below 2.0 will receive academic probation.",
            category="Academic", is_active=True, created_by=admin.id),
        FAQ(question="How do I get my official transcript?",
            answer="Submit Form TR-01 to the department office. Processing takes 5-7 working days. Rush processing (2 days) is available at additional cost.",
            category="Administrative", is_active=True, created_by=admin.id),
        FAQ(question="What is the attendance policy?",
            answer="Minimum 75% attendance is required to sit for final exams. Below 75% results in automatic NC (Not Complete) grade. Medical certificates must be submitted within 3 working days.",
            category="Exams", is_active=True, created_by=admin.id),
        FAQ(question="When are tuition fees due?",
            answer="Fees are due within the first 2 weeks of each semester. Late payment incurs a 2% monthly surcharge. Scholarship students must confirm renewal annually.",
            category="Fees", is_active=True, created_by=admin.id),
        FAQ(question="Can I take courses from other departments?",
            answer="Yes, with advisor approval. Elective slots allow up to 2 courses from other departments per semester, subject to prerequisites.",
            category="Academic", is_active=True, created_by=admin.id),
    ]
    db.add_all(faqs)

    procedures = [
        Procedure(
            title="Thesis Submission Process", category="Academic",
            steps=["Get supervisor approval by November 30", "Upload soft copy to portal by December 15",
                   "Submit 3 hard copies to department office by December 17",
                   "Pay binding fee at accounts section", "Collect receipt and submit to coordinator"],
            is_active=True, created_by=admin.id
        ),
        Procedure(
            title="Course Waiver Application", category="Administrative",
            steps=["Obtain Form DW-01 from department office",
                   "Attach syllabi from equivalent course at previous institution",
                   "Get supervisor signature", "Submit to Academic Section before add/drop deadline",
                   "Await 7-10 day processing time"],
            is_active=True, created_by=admin.id
        ),
        Procedure(
            title="Official Transcript Request", category="Administrative",
            steps=["Fill Form TR-01 at department office", "Pay applicable fee at accounts",
                   "Attach payment receipt to form", "Submit to department office",
                   "Collect after 5-7 working days"],
            is_active=True, created_by=admin.id
        ),
    ]
    db.add_all(procedures)
    db.commit()
    return {"message": "Database seeded successfully", "faqs": len(faqs), "procedures": len(procedures)}
