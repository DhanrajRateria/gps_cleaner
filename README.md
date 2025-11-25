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
```

## Output
Processed JSON and GeoJSON including:

- Raw route (LineString)
- Cleaned route (LineString)
- Jitter points (Point features)
- Idling points (Point features with duration)

## Quick Start
CLI
```bash

# Create venv & install deps
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run command-line pipeline (sample input and default config)
python -m gps_cleaner.pipeline \
  --input data/sample/sample_raw.json \
  --output data/sample/processed.json \
  --config configs/default.yaml
```
```bash

# Start Flask server
PYTHONPATH=src flask --app gps_cleaner.web.app run --host 0.0.0.0 --port 8000

# Open in browser
http://localhost:8000
```

- Upload your JSON file from the index page
- View raw & processed layers on the interactive map

Configuration
Edit configs/default.yaml for thresholds:

- max_speed_kmh
- speed_mad_threshold
- bearing_change_threshold_deg
- hampel_window_size
- hampel_n_sigma
- ema_alpha
- idle_speed_kmh
- idle_min_duration_sec

## Tests
```bash
docker build -t gps-cleaner:latest .docker run -it --rm -p 8000:8000 -v "$PWD/data":/app/data gps-cleaner:latest
```

## Notes

- Leaflet loads from CDN; internet is required to fetch Leaflet assets.
- Time parsing expects ISO-8601 with timezone (e.g., +00:00).

## License
MIT