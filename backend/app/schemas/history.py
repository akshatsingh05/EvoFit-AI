from datetime import date as date_, datetime
from pydantic import BaseModel


class HistoryEntry(BaseModel):
    """
    One row in any "history" list. Domain services (workout_service,
    nutrition_service, and later daily_checkin_service / adaptive_service for
    Recovery) each build a list[HistoryEntry] from their own models — this
    schema is the only thing routers and the frontend need to agree on, so a
    new history type is "write an adapter function", not "invent a new shape".
    """

    period_start: date_
    period_end: date_
    title: str  # e.g. "Week of Jun 2" or "Jun 9"
    summary: str  # short human-readable summary, e.g. "5 workout days · 4 completed"
    created_at: datetime
    detail_ref: str  # opaque identifier the frontend can use to jump back into that period (e.g. week_start_date)


class HistoryListResponse(BaseModel):
    kind: str  # "workout" | "nutrition" | "daily_checkin" | "recovery"
    entries: list[HistoryEntry]
