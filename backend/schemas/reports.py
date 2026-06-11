from pydantic import BaseModel


class ReportSummary(BaseModel):
    total_tickets: int
    by_source: dict[str, int]
    by_status: dict[str, int]
    by_category: dict[str, int]
    high_risk_total: int
    high_risk_pending_approval: int
    sla_breached: int
    avg_resolution_hours: float
