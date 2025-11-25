import argparse
from typing import List

from .config import load_config
from .io import load_json_points, save_json, to_processed_json
from .jitter_detection import JitterDetector
from .smoothing import RouteSmoother
from .idling import IdlingDetector
from .models import ProcessedResult


def run_pipeline(input_path: str, output_path: str, config_path: str) -> ProcessedResult:
    cfg = load_config(config_path)
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
    idling_points = id_detector.detect(points)  # Detect idling on raw points (configurable choice)

    result = ProcessedResult(
        raw_points=points,
        cleaned_points=cleaned_points,
        jitter_point_ids=jitter_ids,
        idling_points=idling_points,
    )

    save_json(output_path, to_processed_json(result))
    return result


def main():
    parser = argparse.ArgumentParser(description="GPS cleaner: jitter removal, smoothing, idling detection")
    parser.add_argument("--input", required=True, help="Path to input JSON file containing GPS pings")
    parser.add_argument("--output", required=True, help="Path to output processed JSON file")
    parser.add_argument("--config", required=True, help="Path to YAML config file with thresholds")

    args = parser.parse_args()
    run_pipeline(args.input, args.output, args.config)


if __name__ == "__main__":
    main()
