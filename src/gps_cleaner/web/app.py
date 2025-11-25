from flask import Flask, render_template, request, jsonify, redirect, url_for
from pathlib import Path
import tempfile

from gps_cleaner.config import load_config
from gps_cleaner.pipeline import run_pipeline
from gps_cleaner.io import load_json_points, to_geojson
from gps_cleaner.jitter_detection import JitterDetector
from gps_cleaner.smoothing import RouteSmoother
from gps_cleaner.idling import IdlingDetector
from gps_cleaner.models import ProcessedResult

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)

# Keep last result in memory for visualization
_last_result: ProcessedResult | None = None


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    global _last_result
    file = request.files.get("file")
    if not file:
        return redirect(url_for("index"))

    # Save uploaded file to temp
    temp_dir = Path(tempfile.mkdtemp())
    input_path = temp_dir / "uploaded.json"
    file.save(str(input_path))

    config_path = Path("configs/default.yaml")
    cfg = load_config(config_path)

    # Run in-memory pipeline
    points = load_json_points(input_path)
    jd = JitterDetector(
        max_speed_kmh=cfg.max_speed_kmh,
        speed_mad_threshold=cfg.speed_mad_threshold,
        bearing_change_threshold_deg=cfg.bearing_change_threshold_deg,
        min_distance_meters=cfg.min_distance_meters,
        hampel_window_size=cfg.hampel_window_size,
        hampel_n_sigma=cfg.hampel_n_sigma,
    )
    jitter_flags = jd.detect(points)
    jitter_ids = [p.id for p, flag in zip(points, jitter_flags) if flag]

    smoother = RouteSmoother(ema_alpha=cfg.ema_alpha)
    cleaned_points = smoother.smooth(points, jitter_flags)

    id_detector = IdlingDetector(idle_speed_kmh=cfg.idle_speed_kmh, idle_min_duration_sec=cfg.idle_min_duration_sec)
    idling_points = id_detector.detect(points)

    _last_result = ProcessedResult(
        raw_points=points,
        cleaned_points=cleaned_points,
        jitter_point_ids=jitter_ids,
        idling_points=idling_points,
    )
    return render_template("map.html")


@app.route("/api/processed", methods=["GET"])
def api_processed():
    global _last_result
    if _last_result is None:
        return jsonify({"error": "No processed data available. Upload a JSON file first."}), 400
    geojson = to_geojson(_last_result)
    return jsonify(geojson)


@app.route("/sample", methods=["GET"])
def sample():
    global _last_result
    cfg = load_config("configs/default.yaml")
    result = run_pipeline("data/sample/sample_raw.json", "data/sample/processed.json", "configs/default.yaml")
    _last_result = result
    return render_template("map.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
