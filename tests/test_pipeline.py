from pathlib import Path
from gps_cleaner.pipeline import run_pipeline

def test_pipeline_runs(tmp_path: Path):
    input_path = Path("data/sample/sample_raw.json")
    output_path = tmp_path / "processed.json"
    config_path = Path("configs/default.yaml")

    result = run_pipeline(str(input_path), str(output_path), str(config_path))
    assert len(result.raw_points) > 0
    assert output_path.exists()
    # cleaned points should be <= raw points
    assert len(result.cleaned_points) <= len(result.raw_points)
    # jitter ids list exists
    assert isinstance(result.jitter_point_ids, list)
