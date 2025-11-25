FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY configs /app/configs
COPY src /app/src
COPY data /app/data

ENV PYTHONPATH=/app/src
ENV FLASK_APP=gps_cleaner.web.app

EXPOSE 8000

CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]