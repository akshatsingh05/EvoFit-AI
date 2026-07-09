# --- Backend production image (FastAPI + Gunicorn/Uvicorn) --------------
FROM python:3.12-slim

WORKDIR /app

# System deps needed to build psycopg2-binary's transitive requirements on
# some architectures, plus OCR/PDF support for Sprint 5 plan import
# (tesseract-ocr for image OCR, poppler-utils for scanned-PDF rasterization).
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 tesseract-ocr poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home appuser
USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# Migrations run before the server starts so the schema is always current
# for the image being deployed (see DATABASE_MIGRATION_GUIDE.md).
CMD alembic upgrade head && gunicorn app.main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --access-logfile - \
    --error-logfile -
