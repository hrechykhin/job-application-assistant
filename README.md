# Job Application Assistant

> Track your job search, tailor your CV with AI, and generate cover letters — built for the European job market.

[**Live Demo**](https://accurate-grace-production-abf0.up.railway.app) &nbsp;·&nbsp; [**API Docs**](https://job-application-assistant-production.up.railway.app/docs)

[![CI](https://github.com/hrechykhin/job-application-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/hrechykhin/job-application-assistant/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## Screenshots

<!-- After running the app, take screenshots and save them to docs/screenshots/ -->
<!-- dashboard.png  –  home page with stats cards -->
<!-- kanban.png     –  Application Board with cards in each column -->
<!-- ai-match.png   –  AI job match result panel -->

| Dashboard | Kanban Board | AI Job Match |
|-----------|-------------|--------------|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Kanban](docs/screenshots/kanban.png) | ![AI Match](docs/screenshots/ai-match.png) |

---

## Features

- **Kanban pipeline** — drag-and-drop on desktop and mobile; SAVED → APPLIED → INTERVIEW → OFFER / REJECTED
- **AI job match** — score your CV against a job description; see matched skills, gaps, and suggestions
- **CV tailoring** — AI rewrites your bullet points to match the job requirements
- **Cover letter generation** — full draft generated from your CV + job description
- **Job URL import** — paste a job posting URL; AI extracts title, company, location, and description
- **CV upload** — PDF and DOCX parsing; per-user file storage
- **Profile page** — view and edit your name, see AI quota usage with a live progress bar and reset time
- **JWT authentication** — access + refresh tokens; rate-limited login and registration
- **AI spend controls** — per-user daily quota, input length limits, cached results skip the provider

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query |
| Backend | FastAPI, SQLAlchemy 2, Alembic, Pydantic v2 |
| AI | OpenAI-compatible API (`gpt-4o-mini` by default) |
| Database | PostgreSQL 16 |
| Infra | Docker, Docker Compose, Railway, GitHub Actions CI |

---

## Try the Live Demo

**URL:** https://accurate-grace-production-abf0.up.railway.app

| Field | Value |
|-------|-------|
| Email | `demo@example.com` |
| Password | `Demo1234!` |

The demo account comes pre-loaded with 12 sample applications across all pipeline stages.

---

## Quick Start (local)

**Prerequisites:** Docker + Docker Compose

```bash
git clone https://github.com/hrechykhin/job-application-assistant.git
cd job-application-assistant
cp backend/.env.example backend/.env
# Edit backend/.env — set OPENAI_API_KEY
docker compose up --build
```

Open **http://localhost** in your browser.

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| API docs (Swagger) | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

**Load demo data** (optional):
```bash
docker compose exec backend python seed_demo.py
# Login: demo@example.com / Demo1234!
```

---

## Architecture

```
Browser
  └── nginx (port 80)
        └── React SPA (Vite + TypeScript)
              └── FastAPI backend (port 8000)
                    ├── PostgreSQL (jobs, applications, CVs, AI cache)
                    ├── Local volume (CV file storage)
                    └── OpenAI API (AI features)
```

---

## Project Structure

```
backend/app/
  api/v1/       – route handlers (auth, jobs, applications, cvs, ai)
  services/     – business logic
  models/       – SQLAlchemy ORM models
  schemas/      – Pydantic request/response schemas
  middleware/   – request logging with structured IDs
  core/         – config, security, rate limiter

frontend/src/
  features/     – page-level components (Dashboard, Board, Jobs, Applications)
  api/          – typed axios API clients
  auth/         – JWT auth context + hooks
  components/   – shared UI components
```

---

## Running Tests

```bash
# Backend (SQLite in-memory, no services needed)
cd backend && pytest tests/ -v

# Frontend
cd frontend && npm test -- --run
```

Tests run automatically on every push via GitHub Actions CI.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | required |
| `SECRET_KEY` | JWT signing secret (min 32 chars) | required |
| `OPENAI_API_KEY` | OpenAI or compatible API key | optional |
| `OPENAI_BASE_URL` | API base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | Model to use | `gpt-4o-mini` |
| `AI_ENABLED` | Enable/disable all AI features | `true` |
| `AI_MAX_REQUESTS_PER_DAY` | Per-user daily AI call limit | `50` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FORMAT` | `text` (dev) or `json` (production) | `text` |

See [backend/.env.example](backend/.env.example) for the full list.

---

## License

[MIT](LICENSE)
