"""Query log model for tracking all chat interactions."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    
    # Domain check
    is_in_domain = Column(Boolean, default=True)
    domain_score = Column(Float, nullable=True)
    
    # Retrieval
    retrieval_method = Column(String(50), nullable=True)  # faq, rag, hybrid
    sources_used = Column(JSON, default=list)  # list of source filenames
    
    # Performance
    response_time_ms = Column(Integer, nullable=True)
    status = Column(String(20), default="resolved")  # resolved, rejected, failed, partial
    
    # Metadata
    session_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="query_logs")
