# Tiba Mkononi - Healthcare in Your Hands

Backend API for the Tiba Mkononi healthcare platform.
Built with FastAPI, PostgreSQL, Redis, and Gemma 4.

## Quick Start

`ash
# Copy environment file
cp .env.example .env
# Edit .env with your values

# Install dependencies
pip install -r requirements.txt

# Start services
docker-compose up -d db redis minio

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload
API docs: http://localhost:8000/docs

Tech Stack
FastAPI (Python 3.12)

PostgreSQL 16 + PostGIS

Redis

Gemma 4 (Hugging Face)

Celery

Docker
