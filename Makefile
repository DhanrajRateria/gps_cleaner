.PHONY: install test run-cli run-web docker-build docker-run clean

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

test:
	. .venv/bin/activate && pytest -q

run-cli:
	. .venv/bin/activate && python -m gps_cleaner.pipeline --input data/sample/sample_raw.json --output data/sample/processed.json --config configs/default.yaml

run-web:
	. .venv/bin/activate && PYTHONPATH=src flask --app gps_cleaner.web.app run --host 0.0.0.0 --port 8000

docker-build:
	docker build -t gps-cleaner:latest .

docker-run:
	docker run -it --rm -p 8000:8000 -v "$$PWD/data":/app/data gps-cleaner:latest

clean:
	rm -rf .venv __pycache__ .pytest_cache
	find . -name '__pycache__' -type d -exec rm -rf {} +