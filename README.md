
# GPS Cleaner: Jitter Removal, Route Smoothing, Idling Detection, and Leaflet Visualization

This project provides a production-grade pipeline to:
- Identify and mark irregular GPS pings (jitters).
- Smooth the route after removing jitter points.
- Detect idling points (low-speed segments over time).
- Visualize raw vs processed routes on a Leaflet map (with markers).

## Features

- Robust jitter detection using speed outliers (median & MAD), hard speed limit, bearing-change thresholds, and Hampel filtering.
- Conservative criteria to avoid false positives.
- Exponential moving average (EMA) smoothing on non-jitter points.
- Idling detection for stationary periods longer than a configured minimum duration.
- CLI pipeline and Flask-based web app.
- GeoJSON export for mapping layers.
- Configuration file for thresholds.
- Unit tests included.

## Input Format
JSON array of objects:
```json
[
  {
    "id": "44e06249-5881-44c2-b017-4b0c7ca9b6d8",
    "gpstime": "2025-11-13 01:15:16+00:00",
    "lat": 19.4591066666667,
    "lon": 72.8851966666667
  },
  {
    "id": "ec544fa9-d96c-427c-8094-3df1a5e2c54a",
    "gpstime": "2025-11-13 01:16:02+00:00",
    "lat": 19.461915,
    "lon": 72.8867883333333
  }
]
