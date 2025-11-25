import math
from gps_cleaner.utils_geo import haversine_distance_m, bearing_deg, robust_z_scores, exponential_moving_average

def test_haversine_distance():
    # Approx distance between two nearby points
    lat1, lon1 = 19.4591066667, 72.8851966667
    lat2, lon2 = 19.4599066667, 72.8858966667
    d = haversine_distance_m(lat1, lon1, lat2, lon2)
    assert d > 0
    assert 50 < d < 2000

def test_bearing_deg_range():
    b = bearing_deg(19.4591, 72.8852, 19.4607, 72.8866)
    assert 0 <= b <= 360

def test_robust_z_scores_zero_mad():
    z = robust_z_scores([1, 1, 1, 1])
    assert all(abs(v) < 1e-6 for v in z)

def test_ema_basic():
    arr = [0, 10, 20]
    ema = exponential_moving_average(arr, alpha=0.5)
    assert len(ema) == 3
    assert abs(ema[-1] - 15) < 1e-6
