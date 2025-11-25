from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Ping:
    id: str
    gpstime: datetime
    lat: float
    lon: float


@dataclass
class IdlingPoint:
    lat: float
    lon: float
    start_time: datetime
    end_time: datetime
    duration_sec: float
    count: int


@dataclass
class ProcessedResult:
    raw_points: List[Ping]
    cleaned_points: List[Ping]
    jitter_point_ids: List[str]
