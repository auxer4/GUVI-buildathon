from pydantic import BaseModel
from datetime import datetime


class Event(BaseModel):
    event_id: str
    event_type: str
    source: str
    payload: dict
    timestamp: datetime
