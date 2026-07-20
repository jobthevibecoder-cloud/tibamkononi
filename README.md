---
title: Tiba Mkononi API
emoji: 🏥
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
license: apache-2.0
---

# Tiba Mkononi API

Healthcare in Your Hands - Backend API for the Tiba Mkononi platform.

## Endpoints

- `/docs` - Swagger API documentation
- `/health` - Health check
- `/v1/hospitals/` - Hospital management
- `/v1/triage/analyze` - AI symptom analysis
- `/v1/emergency/analyze` - Emergency processing
- `/v1/appointments/` - Appointment booking
- `/v1/county/dashboard` - County director dashboard

## Tech Stack

- FastAPI (Python 3.12)
- SQLite Database
- Gemma 4 AI (Hugging Face Inference API)
