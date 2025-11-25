from typing import List

from .models import Ping
from .utils_geo import exponential_moving_average


class RouteSmoother:
    """
    Smooth the route using Exponential Moving Average (EMA) applied
    to non-jitter points, preserving timestamps and IDs.
    """

    def __init__(self, ema_alpha: float):
        self.ema_alpha = ema_alpha

    def smooth(self, points: List[Ping], jitter_flags: List[bool]) -> List[Ping]:
        if not points:
            return []

        # Remove jitter points
        kept = [p for p, flag in zip(points, jitter_flags) if not flag]
        if not kept:
            return []

        lats = [p.lat for p in kept]
        lons = [p.lon for p in kept]

        lats_sm = exponential_moving_average(lats, self.ema_alpha)
        lons_sm = exponential_moving_average(lons, self.ema_alpha)

        smoothed = []
        for p, lat_sm, lon_sm in zip(kept, lats_sm, lons_sm):
            smoothed.append(Ping(id=p.id, gpstime=p.gpstime, lat=lat_sm, lon=lon_sm))

        return smoothed
