from datetime import datetime, timezone, timedelta
from gps_cleaner.models import Ping
from gps_cleaner.idling import IdlingDetector

def make_ping(pid, t, lat, lon):
    return Ping(id=pid, gpstime=t, lat=lat, lon=lon)

def test_idling_detection_duration():
    base = datetime(2025, 11, 13, 1, 0, 0, tzinfo=timezone.utc)
    points = [
        make_ping("p1", base, 19.4591, 72.8852),
        make_ping("p2", base + timedelta(minutes=1), 19.4592, 72.8853),
        make_ping("p3", base + timedelta(minutes=3), 19.4592, 72.8853),  # idle (no movement)
        make_ping("p4", base + timedelta(minutes=5), 19.4592, 72.8853),  # idle continues
        make_ping("p5", base + timedelta(minutes=7), 19.4600, 72.8860),  # moves
    ]

    det = IdlingDetector(idle_speed_kmh=3, idle_min_duration_sec=120)  # 2 minutes
    idles = det.detect(points)
    assert len(idles) >= 1
    # Duration ~ 4 minutes
    assert idles[0].duration_sec >= 240 - 5  # tolerance
