# Job Application Assistant

An AI-powered job application assistant focused on the European job market. Upload your CV, target jobs, get AI analysis and tailoring suggestions, generate cover letters, and track your applications in a kanban pipeline.

---

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  React SPA  │────▶│  FastAPI Backend  │────▶│  PostgreSQL  │
│ (Vite + TS) │     │   /api/v1         │     │              │
└─────────────┘     └──────────────────┘     └──────────────┘
                             │
                             ├──▶  Local volume (CV file storage)
                             └──▶  OpenAI API (AI features)
```

**Backend modules:**
- `auth` — JWT register/login/refresh
- `users` — profile management
- `cvs` — upload to local volume, PDF/DOCX text extraction
- `jobs` — CRUD for target job descriptions; URL import via AI
- `applications` — kanban board + workspace with reminders
- `ai` — job match analysis, CV tailoring, cover letter generation

---

## Local Setup

### Prerequisites
- Docker + Docker Compose
- An OpenAI API key (or compatible endpoint)

### 1. Clone and configure

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your keys
```

### 2. Start the full stack

```bash
docker-compose up --build
```

This starts:
- **PostgreSQL** on port 5432
- **FastAPI backend** on port 8000 (auto-runs Alembic migrations)
- **React frontend** on port 80

### 3. Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| API docs | http://localhost:8000/docs |
| Backend health | http://localhost:8000/health |

### Running backend locally (without Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in DATABASE_URL etc.

alembic upgrade head
uvicorn app.main:app --reload
```

### Running frontend locally

```bash
cd frontend
npm install
cp .env.example .env.local   # set VITE_API_BASE_URL=http://localhost:8000/api/v1
npm run dev
```

---

## File Storage

CV files are stored on the **local filesystem** inside the Docker volume `uploads_data`, mounted at `/app/uploads`. No cloud storage is needed.

The file key format is: `cvs/{user_id}/{uuid}/{original_filename}`

To back up uploaded CVs, back up the Docker volume or the host path you bind-mount.

---

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | required |
| `SECRET_KEY` | JWT signing secret (min 32 chars) | required |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `STORAGE_PATH` | Local path for CV uploads | `/app/uploads` |
| `OPENAI_API_KEY` | OpenAI or compatible API key | optional |
| `OPENAI_BASE_URL` | API base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | Model to use | `gpt-4o-mini` |
| `AI_ENABLED` | Enable/disable all AI features | `true` |
| `AI_MAX_REQUESTS_PER_DAY` | Max AI calls per user per day | `50` |
| `AI_MAX_CV_CHARS` | Max CV text length (chars) accepted | `6000` |
| `AI_MAX_JOB_CHARS` | Max job description length (chars) accepted | `4000` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `/api/v1` |

---

## How AI Integration Works

The AI layer is in `backend/app/integrations/ai_client.py`. It is provider-agnostic:

1. `AIClientBase` defines the interface (`chat(system, user) -> AIResponse`)
2. `OpenAIClient` implements it using the OpenAI SDK with `response_format: json_object`
3. To swap providers, implement `AIClientBase` and update `get_ai_client()`

**Four AI operations:**

| Endpoint | Input | Output |
|----------|-------|--------|
| `POST /ai/job-match` | cv_id + job_id | match score, matched/missing skills, suggestions |
| `POST /ai/cv-tailoring` | cv_id + job_id | bullet improvements, keywords, summary tweaks |
| `POST /ai/cover-letter` | cv_id + job_id | full cover letter draft |
| `POST /jobs/import-url` | url | pre-filled title, company, location, description |

**Results are cached** in the `ai_analyses` table (per cv+job+type+prompt_version). Re-running the same job-match or CV-tailoring returns the cached result. Cover letters are always regenerated.

**Honesty constraints** are embedded in every system prompt:
- The AI may not invent skills, experience, degrees, or certifications
- It may only rephrase or reorder what is in the CV
- Gaps are surfaced as suggestions, not presented as facts
- All outputs carry a disclaimer

### AI Spend Control

Because the app uses your own API key, usage is protected:

- **`AI_ENABLED=false`** — disables all AI endpoints globally (returns 503)
- **`AI_MAX_REQUESTS_PER_DAY`** — per-user daily call limit (returns 429 when exceeded)
- **`AI_MAX_CV_CHARS` / `AI_MAX_JOB_CHARS`** — input length limits; oversized inputs are rejected before any provider call (returns 422)
- **Cached results** do not consume quota — only real provider calls are counted
- Each provider call is logged in the `ai_usage_logs` table with token counts and model name

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

Tests use an in-memory SQLite database (no external services needed). AI provider calls are mocked.

---

## GDPR Notes

- Users can delete their own CVs (`DELETE /api/v1/cvs/{id}`) — this removes the file from the local volume and the DB record
- Users can delete jobs and applications
- CV text is stored in the database for AI processing; consider encrypting the volume at rest
- AI providers may retain prompts per their own data policies — review OpenAI's data handling if processing EU personal data
- Raw CV text and job descriptions are not logged

---

## Tradeoffs & MVP Limitations

| Area | Decision | Reason |
|------|----------|--------|
| Auth | Stateless JWT (no revocation) | Simpler for MVP; add a token blocklist (Redis) for production |
| Refresh tokens | Stateless | Same; consider storing in DB for true revocation |
| AI caching | Per-version cache in PG | Avoids repeat API calls; invalidated by bumping `PROMPT_VERSION` |
| CV parsing | pdfminer for PDF, python-docx for DOCX | Good enough for MVP; consider Apache Tika for edge cases |
| AI quota | Daily count per user | Simple and effective; does not reset mid-day |
| File storage | Local Docker volume | Simple; no cloud dependencies |
| Rate limiting | Not implemented on auth endpoints | Add `slowapi` for production |
| Email notifications | Not implemented | Stub hook in application service |
| File type validation | Extension + MIME type | Add magic-byte validation for production |

---

## Recommended Next Features

### 1. Editable AI Outputs
Let users edit and save the generated cover letter and tailored content. Store the user-edited version separately from the raw AI output so the final document they send is tracked.

### 2. Run-All AI Flow
One "Analyse this application" button that triggers job match, CV tailoring, and cover letter generation together for a selected CV + job pair, instead of three separate actions.

### 3. Magic-byte file validation
Add MIME type validation based on file content (not just extension) for uploaded CVs. Prevents mismatched or malicious files.
