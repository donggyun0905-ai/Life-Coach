from pydantic import BaseModel
from typing import Dict, List, Optional

class DailySummaryDTO(BaseModel):
    date: str
    steps: Optional[int] = None
    hrAvg: Optional[float] = None
    hrRestAvg: Optional[float] = None
    sleepMinutes: Optional[int] = None
    sleepStages: Optional[Dict[str, int]] = None  # {"light":220,"deep":70,"rem":90,"awake":15}

class HcIngestDTO(BaseModel):
    user_id: str
    summaries: List[DailySummaryDTO]
