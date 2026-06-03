# Multi-stage build for production Django application
FROM python:3.11-slim AS builder

WORKDIR /build

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --user --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

COPY --from=builder /root/.local /root/.local
COPY --from=builder /build /app

RUN mkdir -p logs media staticfiles
RUN python manage.py collectstatic --noinput --clear

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/', timeout=5)"

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "config.wsgi:application"]
