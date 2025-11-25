import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from dateutil import parser

from .models import Ping, ProcessedResult, IdlingPoint


def load_json_points(path: str | Path) -> List[Ping]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    points: List[Ping] = []
    for item in data:
        pid = str(item["id"])
        gpstime = parser.isoparse(str(item["gpstime"]))
        lat = float(item["lat"])
        lon = float(item["lon"])
        points.append(Ping(id=pid, gpstime=gpstime, lat=lat, lon=lon))

    # Ensure sorted by time
    points.sort(key=lambda x: x.gpstime)
    return points


def save_json(path: str | Path, obj: Dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=_json_default)


def _json_default(o):
    if isinstance(o, datetime):
        return o.isoformat()
    return str(o)


def to_processed_json(result: ProcessedResult) -> Dict[str, Any]:
    return {
        "raw_points": [
            {"id": p.id, "gpstime": p.gpstime.isoformat(), "lat": p.lat, "lon": p.lon}
            for p in result.raw_points
        ],
        "cleaned_points": [
            {"id": p.id, "gpstime": p.gpstime.isoformat(), "lat": p.lat, "lon": p.lon}
            for p in result.cleaned_points
        ],
        "jitter_point_ids": result.jitter_point_ids,
        "idling_points": [
            {
                "lat": ip.lat,
                "lon": ip.lon,
                "start_time": ip.start_time.isoformat(),
                "end_time": ip.end_time.isoformat(),
                "duration_sec": ip.duration_sec,
                "count": ip.count,
            }
            for ip in result.idling_points
        ],
    }


def to_geojson(result: ProcessedResult) -> Dict[str, Any]:
    """
    Build a GeoJSON FeatureCollection with layers:
    - Raw route LineString
    - Cleaned route LineString
    - Jitter points as Point features
    - Idling points as Point features
    """
    raw_coords = [[p.lon, p.lat] for p in result.raw_points]
    cleaned_coords = [[p.lon, p.lat] for p in result.cleaned_points]

    jitter_ids = set(result.jitter_point_ids)
    jitter_features = []
    for p in result.raw_points:
        if p.id in jitter_ids:
            jitter_features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [p.lon, p.lat]},
                    "properties": {"id": p.id, "gpstime": p.gpstime.isoformat(), "type": "jitter"},
                }
            )

    idling_features = []
    for ip in result.idling_points:
        idling_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [ip.lon, ip.lat]},
                "properties": {
                    "type": "idling",
                    "start_time": ip.start_time.isoformat(),
                    "end_time": ip.end_time.isoformat(),
                    "duration_sec": ip.duration_sec,
                    "count": ip.count,
                },
            }
        )

    fc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": raw_coords},
                "properties": {"layer": "raw_route"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": cleaned_coords},
                "properties": {"layer": "cleaned_route"},
            },
            *jitter_features,
            *idling_features,
        ],
    }
    return fc
