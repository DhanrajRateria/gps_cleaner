import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class Config:
    max_speed_kmh: float
    speed_mad_threshold: float
    bearing_change_threshold_deg: float
    min_distance_meters: float
    hampel_window_size: int
    hampel_n_sigma: float
    ema_alpha: float
    idle_speed_kmh: float
    idle_min_duration_sec: float

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Config":
        return Config(
            max_speed_kmh=float(d.get("max_speed_kmh", 180)),
            speed_mad_threshold=float(d.get("speed_mad_threshold", 3.5)),
            bearing_change_threshold_deg=float(d.get("bearing_change_threshold_deg", 60)),
            min_distance_meters=float(d.get("min_distance_meters", 3)),
            hampel_window_size=int(d.get("hampel_window_size", 5)),
            hampel_n_sigma=float(d.get("hampel_n_sigma", 3)),
            ema_alpha=float(d.get("ema_alpha", 0.25)),
            idle_speed_kmh=float(d.get("idle_speed_kmh", 3)),
            idle_min_duration_sec=float(d.get("idle_min_duration_sec", 120)),
        )


def load_config(path: str | Path) -> Config:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Config.from_dict(data)
