# PostPix API image (P33).
#
# API only: the React app is built separately and served from S3 + CloudFront,
# so nothing from react-app/ is copied in. Only the Python code, the migrations
# and two small start-up scripts are in the image (see .dockerignore, which is
# an allowlist).
#
# Build and run (Docker Desktop on an Apple-silicon Mac builds linux/arm64,
# which matches a Graviton EC2 such as t4g.*):
#   docker build -t postpix-api .
#   docker run --rm -p 8000:8000 --env-file .env postpix-api
# From an x86 machine, build for Graviton with:
#   docker buildx build --platform linux/arm64 -t postpix-api .
ARG PYTHON_VERSION=3.12

# ---- Stage 1: install the pinned packages into a virtualenv ---------------
# Every package in requirements.txt ships a prebuilt wheel (psycopg[binary],
# Pillow, ...), so no compiler is needed; the separate stage keeps pip itself
# and its temporary files out of the final image.
FROM python:${PYTHON_VERSION}-slim AS build
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
COPY requirements.txt /tmp/requirements.txt
RUN /opt/venv/bin/pip install --no-compile -r /tmp/requirements.txt

# ---- Stage 2: runtime ------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app \
    FLASK_ENV=production \
    PORT=8000

# Unprivileged user. The code stays owned by root (read-only for the app);
# only /app/instance (Flask's instance folder) and /data (local SQLite volume
# in docker compose) are writable.
RUN groupadd --system --gid 10001 postpix \
 && useradd --system --uid 10001 --gid postpix --home-dir /app --no-create-home \
            --shell /usr/sbin/nologin postpix \
 && mkdir -p /app/instance /data \
 && chown postpix:postpix /app/instance /data

WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY app/ app/
COPY migrations/ migrations/
COPY wsgi.py gunicorn.conf.py ./
COPY docker/entrypoint.sh docker/healthcheck.py /usr/local/bin/
RUN chmod 0755 /usr/local/bin/entrypoint.sh /usr/local/bin/healthcheck.py

# Numeric id (the postpix user above), so tools that check "runs as non-root"
# do not need to look the name up.
USER 10001:10001
EXPOSE 8000

# GET /api/health (no database, no login). The slim image has no curl, so the
# check is a few lines of Python.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["python", "/usr/local/bin/healthcheck.py"]

# entrypoint.sh can run `flask db upgrade` / `flask seed all` first
# (RUN_MIGRATIONS=1 / SEED_ON_START=1, both off by default), then starts CMD.
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
