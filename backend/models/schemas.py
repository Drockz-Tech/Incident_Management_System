from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, Dict
from backend.models.domain import IncidentState, AlertLevel

class SignalPayload(BaseModel):
    component_id: str
    error_type: str
    latency_ms: Optional[float] = None
    message: str
    metadata: Optional[Dict[str, Any]] = None

class RCARequest(BaseModel):
    start_time: datetime
    end_time: datetime
    category: str
    fix_applied: str
    prevention_steps: str

class StateTransitionRequest(BaseModel):
    state: IncidentState
    rca: Optional[RCARequest] = None

class WorkItemResponse(BaseModel):
    id: str
    component_id: str
    state: IncidentState
    alert_level: AlertLevel
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RCAResponse(RCARequest):
    id: str
    work_item_id: str
    
    class Config:
        from_attributes = True
