from datetime import datetime, timezone, timedelta
from gps_cleaner.models import Ping
from gps_cleaner.jitter_detection import JitterDetector

def make_ping(pid, t, lat, lon):
    return Ping(id=pid, gpstime=t, lat=lat, lon=lon)

def test_jitter_detection_spike():
    base = datetime(2025, 11, 13, 1, 0, 0, tzinfo=timezone.utc)
    points = [
        make_ping("p1", base, 19.4591, 72.8852),
        make_ping("p2", base + timedelta(minutes=1), 19.4599, 72.8860),
        # jitter spike: big jump in 4 seconds
        make_ping("j1", base + timedelta(minutes=1, seconds=4), 19.4700, 72.9000),
        make_ping("p3", base + timedelta(minutes=2), 19.4607, 72.8866),
    ]

    jd = JitterDetector(
        max_speed_kmh=180,
        speed_mad_threshold=3.5,
        bearing_change_threshold_deg=60,
        min_distance_meters=3,
        hampel_window_size=5,
        hampel_n_sigma=3,
    )
    flags = jd.detect(points)
    # Expect the spike point marked as jitter
    assert flags[2] is True
    # Normal points should not be flagged
    assert flags[0] is False
    assert flags[1] is False
