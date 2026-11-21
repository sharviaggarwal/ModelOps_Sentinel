
from typing import TypedDict, Optional, Any


class InvestigationState(TypedDict):
    incident_id: int

    incident: Optional[dict]
    monitoring_report: Optional[dict]

    investigation: Optional[str]
    root_cause: Optional[str]
    supporting_evidence: Optional[list[str]]
    recommendations: Optional[list[str]]
    potential_impact: Optional[str]

    approval_status: Optional[str]
    error: Optional[str]