FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080 \
    VERMUTEN_CONFIG=demo.json

WORKDIR /app

# All dependencies ship as wheels, so no compiler is needed in the image.
COPY requirements.txt .
RUN pip install -r requirements.txt \
    && useradd --create-home --uid 10001 vermuten

COPY --chown=root:root app.py demo.json ./
COPY --chown=root:root application ./application
COPY --chown=root:root static ./static
COPY --chown=root:root templates ./templates

USER 10001
EXPOSE 8080

# Game state lives in memory: exactly one worker process, threads for concurrency.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --access-logfile - app:app"]
