FROM python:3.12-slim

# Don't buffer stdout/stderr (so logs show up immediately), no .pyc files.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# Install Python dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application (the built static/css/app.css is committed,
# so no Node/Tailwind build is needed at image build time).
COPY . .

EXPOSE 8000

# Use shell form so $PORT is expanded at runtime (Coolify injects it).
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
