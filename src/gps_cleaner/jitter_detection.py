from typing import List, Tuple

from .models import Ping
from .utils_geo import (
    haversine_distance_m,
    bearing_deg,
    speeds_kmh,
    compute_bearing_changes,
    robust_z_scores,
    hampel_outliers,
)


class JitterDetector:
    """
    Detect jitter (irregular GPS pings) using a conservative, multi-signal approach:
    - Robust z-score on speed using median & MAD
    - Hard maximum speed threshold
    - Large instantaneous bearing change coupled with small movement
    - Hampel filter on lat/lon series
    """

    def __init__(
        self,
        max_speed_kmh: float,
        speed_mad_threshold: float,
        bearing_change_threshold_deg: float,
        min_distance_meters: float,
        hampel_window_size: int,
        hampel_n_sigma: float,
    ):
        self.max_speed_kmh = max_speed_kmh
        self.speed_mad_threshold = speed_mad_threshold
        self.bearing_change_threshold_deg = bearing_change_threshold_deg
        self.min_distance_meters = min_distance_meters
        self.hampel_window_size = hampel_window_size
        self.hampel_n_sigma = hampel_n_sigma

    def detect(self, points: List[Ping]) -> List[bool]:
        n = len(points)
        if n < 3:
            return [False] * n

        lats = [p.lat for p in points]
        lons = [p.lon for p in points]

        # Distances and time deltas
        distances_m = [0.0]
        deltas_s = [0.0]
        bearings = [0.0]
        for i in range(1, n):
            d = haversine_distance_m(lats[i - 1], lons[i - 1], lats[i], lons[i])
            dt = (points[i].gpstime - points[i - 1].gpstime).total_seconds()
            distances_m.append(d)
            deltas_s.append(max(dt, 0.0))
            bearings.append(bearing_deg(lats[i - 1], lons[i - 1], lats[i], lons[i]))

        speeds = speeds_kmh(distances_m, deltas_s)
        bearing_changes = compute_bearing_changes(bearings)

        speed_z = robust_z_scores(speeds)
        lat_hampel = hampel_outliers(lats, self.hampel_window_size, self.hampel_n_sigma)
        lon_hampel = hampel_outliers(lons, self.hampel_window_size, self.hampel_n_sigma)

        flags = [False] * n

        for i in range(n):
            signals = 0

            # Signal A: Excessive speed
            if speeds[i] > self.max_speed_kmh or abs(speed_z[i]) > self.speed_mad_threshold:
                signals += 1

            # Signal B: Abrupt direction change with tiny movement (typical jitter)
            if (bearing_changes[i] > self.bearing_change_threshold_deg) and (distances_m[i] < self.min_distance_meters):
                signals += 1

            # Signal C: Hampel filter outlier in lat/lon
            if lat_hampel[i] or lon_hampel[i]:
                signals += 1

            # Conservative: Require at least 2 signals to mark jitter
            flags[i] = signals >= 2

        # Do not flag first point as jitter unless very strong signals (override case)
        if n > 0 and flags[0]:
            # mitigate false positive on first ping
            flags[0] = False

        return flags
