
#!/usr/bin/env bash
set -euo pipefail

INPUT=${1:-data/sample/sample_raw.json}
OUTPUT=${2:-data/sample/processed.json}
CONFIG=${3:-configs/default.yaml}

PYTHONPATH=src python -m gps_cleaner.pipeline --input "$INPUT" --output "$OUTPUT" --config "$CONFIG"
echo "Processed file written to: $OUTPUT"
