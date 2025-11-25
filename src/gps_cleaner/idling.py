from typing import List

from .models import Ping, IdlingPoint
from .utils_geo import haversine_distance_m, speeds_kmh


class IdlingDetector:
    """
    Detect idling segments where speed < idle_speed_kmh for duration >= idle_min_duration_sec.
    Produces representative points with centroid coordinates and time range.
    """

    def __init__(self, idle_speed_kmh: float, idle_min_duration_sec: float):
        self.idle_speed_kmh = idle_speed_kmh
        self.idle_min_duration_sec = idle_min_duration_sec

    def detect(self, points: List[Ping]) -> List[IdlingPoint]:
        n = len(points)
        if n < 2:
            return []

        # Compute segment speeds and deltas
        distances_m = [0.0]
        deltas_s = [0.0]
        for i in range(1, n):
            d = haversine_distance_m(points[i - 1].lat, points[i - 1].lon, points[i].lat, points[i].lon)
            dt = (points[i].gpstime - points[i - 1].gpstime).total_seconds()
            distances_m.append(d)
            deltas_s.append(max(dt, 0.0))

        speeds = speeds_kmh(distances_m, deltas_s)

        idling_points: List[IdlingPoint] = []
        i = 0
        while i < n:
            if speeds[i] < self.idle_speed_kmh:
                # Start of potential idle segment
                j = i
                total_duration = 0.0
                lats = []
                lons = []
                while j < n and speeds[j] < self.idle_speed_kmh:
                    lats.append(points[j].lat)
                    lons.append(points[j].lon)
                    total_duration += deltas_s[j] if j > 0 else 0.0
                    j += 1

                if total_duration >= self.idle_min_duration_sec:
                    # Representative point at centroid; time range from i to j-1
                    lat_c = sum(lats) / len(lats)
                    lon_c = sum(lons) / len(lons)
                    start_time = points[i].gpstime
                    end_time = points[j - 1].gpstime
                    idling_points.append(
                        IdlingPoint(
                            lat=lat_c,
                            lon=lon_c,
                            start_time=start_time,
                            end_time=end_time,
                            duration_sec=total_duration,
                            count=len(lats),
                        )
                    )
                i = j
            else:
                i += 1

