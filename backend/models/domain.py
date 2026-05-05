from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from backend.db.postgres import Base
from datetime import datetime, timezone

class IncidentState(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class AlertLevel(str, enum.Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class WorkItem(Base):
    __tablename__ = "work_items"
    
    id = Column(String, primary_key=True, index=True)
    component_id = Column(String, index=True, nullable=False)
    state = Column(Enum(IncidentState), default=IncidentState.OPEN, nullable=False)
    alert_level = Column(Enum(AlertLevel), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    rca = relationship("RCA", back_populates="work_item", uselist=False, cascade="all, delete")

class RCA(Base):
    __tablename__ = "rcas"
    
    id = Column(String, primary_key=True, index=True)
    work_item_id = Column(String, ForeignKey("work_items.id"), unique=True, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    category = Column(String, nullable=False)
    fix_applied = Column(Text, nullable=False)
    prevention_steps = Column(Text, nullable=False)
    
    work_item = relationship("WorkItem", back_populates="rca")
