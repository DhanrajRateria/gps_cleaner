import math
from typing import List, Tuple

import numpy as np


EARTH_RADIUS_M = 6371000.0  # meters


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two points on Earth (meters).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_M * c


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Initial bearing from point 1 to point 2 (degrees).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)

    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    theta = math.atan2(y, x)
    bearing = (math.degrees(theta) + 360.0) % 360.0
    return bearing


def angular_difference_deg(a: float, b: float) -> float:
    """
    Smallest angular difference between two bearings (degrees).
    """
    diff = (a - b + 180) % 360 - 180
    return abs(diff)


def robust_z_scores(x: List[float]) -> np.ndarray:
    """
    Robust z-score using Median and MAD. Returns z-scores for vector x.
    """
    arr = np.asarray(x, dtype=float)
    median = np.nanmedian(arr)
    mad = np.nanmedian(np.abs(arr - median))
    if mad == 0:
        return np.zeros_like(arr)
    return (arr - median) / (1.4826 * mad)  # 1.4826 ~ scaling factor for MAD


def hampel_outliers(arr: List[float], window_size: int, n_sigma: float) -> List[bool]:
    """
    Hampel filter for outlier detection in a time series.
    Returns a boolean list of outlier flags for each index.
    """
    x = np.asarray(arr, dtype=float)
    n = len(x)
    flags = np.zeros(n, dtype=bool)
    k = window_size

    if k < 3 or k % 2 == 0:
        k = 5  # enforce odd reasonable window

    half = k // 2
    for i in range(n):
        i0 = max(0, i - half)
        i1 = min(n, i + half + 1)
        window = x[i0:i1]
        med = np.nanmedian(window)
        mad = np.nanmedian(np.abs(window - med))
        if mad == 0:
            continue
        z = abs(x[i] - med) / (1.4826 * mad)
        if z > n_sigma:
            flags[i] = True

    return flags.tolist()


def exponential_moving_average(values: List[float], alpha: float) -> List[float]:
    """
    EMA on a list of numeric values.
    """
    if not values:
        return []
    alpha = max(0.0, min(1.0, alpha))
    ema = []
    prev = values[0]
    ema.append(prev)
    for v in values[1:]:
        prev = alpha * v + (1 - alpha) * prev
        ema.append(prev)
    return ema


def speeds_kmh(distances_m: List[float], deltas_s: List[float]) -> List[float]:
    """
    Compute speed in km/h for each segment (distance over time).
    Speed value is assigned to the second point of the segment.
    """
    speeds = []
    for d, t in zip(distances_m, deltas_s):
        if t <= 0:
            speeds.append(0.0)
            continue
        speeds.append((d / t) * 3.6)
    return speeds


def compute_bearing_changes(bearings: List[float]) -> List[float]:
    """
    Bearing change between consecutive bearings; first element is 0.
    """
    bc = [0.0]
    for i in range(1, len(bearings)):
        bc.append(angular_difference_deg(bearings[i], bearings[i - 1]))
