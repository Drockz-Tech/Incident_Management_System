from backend.models.schemas import SignalPayload, RCARequest
from backend.models.domain import AlertLevel, IncidentState, WorkItem, RCA
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

def determine_alert_level(signal: SignalPayload) -> AlertLevel:
    """Strategy for alerting based on component logic."""
    component = signal.component_id.upper()
    if "RDBMS" in component or "DB" in component:
        return AlertLevel.P0
    elif "CACHE" in component:
        return AlertLevel.P2
    elif "API" in component:
        return AlertLevel.P1
    else:
        return AlertLevel.P3

async def transition_state(session: AsyncSession, work_item: WorkItem, new_state: IncidentState, rca_data: RCARequest = None):
    """
    Manage state transitions. OPEN -> INVESTIGATING -> RESOLVED -> CLOSED
    """
    # Load RCA if needed. Assuming it might be loaded or we just check if it exists.
    # To be safe, we check if rca_data is provided when closing.
    
    if new_state == IncidentState.CLOSED:
        if not rca_data and not work_item.rca:
            raise HTTPException(status_code=400, detail="Mandatory RCA is required to close the incident.")
        
        if rca_data:
            rca = RCA(
                id=str(uuid.uuid4()),
                work_item_id=work_item.id,
                start_time=rca_data.start_time,
                end_time=rca_data.end_time,
                category=rca_data.category,
                fix_applied=rca_data.fix_applied,
                prevention_steps=rca_data.prevention_steps
            )
            session.add(rca)
            
    work_item.state = new_state
    session.add(work_item)
    await session.commit()
    return work_item
