# Job Application Assistant

An AI-powered job application assistant focused on the European job market. Upload your CV, target jobs, get AI analysis and tailoring suggestions, generate cover letters, and track your applications in a kanban pipeline.

---

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  React SPA  │────▶│  FastAPI Backend  │────▶│  PostgreSQL  │
│ (Vite + TS) │     │   /api/v1         │     │  (RDS)       │
└─────────────┘     └──────────────────┘     └──────────────┘
      │                      │
      │                      ├──▶  S3 (CV file storage)
      │                      └──▶  OpenAI API (AI features)
      │
   CloudFront + S3 (static hosting in production)
```

**Backend modules:**
- `auth` — JWT register/login/refresh
- `users` — profile management
- `cvs` — upload to S3, PDF/DOCX text extraction
- `jobs` — CRUD for target job descriptions
- `applications` — kanban-style status tracking
- `ai` — job match analysis, CV tailoring, cover letter generation

---

## Local Setup

### Prerequisites
- Docker + Docker Compose
- An OpenAI API key (or compatible endpoint)
- AWS credentials + S3 bucket (optional for local dev — upload will fail without it)

### 1. Clone and configure

```bash
cp .env.example .env
# Edit .env with your keys
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

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | required |
| `SECRET_KEY` | JWT signing secret (min 32 chars) | required |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `AWS_ACCESS_KEY_ID` | AWS credentials | optional |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials | optional |
| `AWS_REGION` | S3 region | `eu-west-1` |
| `S3_BUCKET_NAME` | Bucket for CV files | `job-assistant-cvs` |
| `OPENAI_API_KEY` | OpenAI or compatible API key | optional |
| `OPENAI_BASE_URL` | API base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | Model to use | `gpt-4o-mini` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `/api/v1` |

---

## How AI Integration Works

The AI layer is in `backend/app/integrations/ai_client.py`. It is provider-agnostic:

1. `AIClientBase` defines the interface (`chat(system, user) -> dict`)
2. `OpenAIClient` implements it using the OpenAI SDK with `response_format: json_object`
3. To swap providers, implement `AIClientBase` and update `get_ai_client()`

**Three AI operations:**

| Endpoint | Input | Output |
|----------|-------|--------|
| `POST /ai/job-match` | cv_id + job_id | match score, matched/missing skills, suggestions |
| `POST /ai/cv-tailoring` | cv_id + job_id | bullet improvements, keywords, summary tweaks |
| `POST /ai/cover-letter` | cv_id + job_id | full cover letter draft |

**Results are cached** in the `ai_analyses` table (per cv+job+type+prompt_version). Re-running the same analysis returns the cached result until the prompt version changes.

**Honesty constraints** are embedded in every system prompt:
- The AI may not invent skills, experience, degrees, or certifications
- It may only rephrase or reorder what is in the CV
- Gaps are surfaced as suggestions, not presented as facts
- All outputs carry a disclaimer

---

## AWS Deployment

### Architecture

```
Internet → CloudFront → S3 (static frontend)
Internet → ALB → ECS (FastAPI) → RDS PostgreSQL
                              → S3 (CV files)
```

### Steps

1. **RDS**: Create a PostgreSQL 16 instance. Use a private subnet. Store the connection string in AWS Secrets Manager.

2. **S3 (CVs)**: Create a private bucket. Do NOT enable public access. The backend generates pre-signed URLs for downloads. Set a lifecycle rule to expire orphaned objects.

3. **ECS (backend)**:
   - Build and push the backend Docker image to ECR
   - Create an ECS Fargate task definition
   - Inject secrets via ECS task environment or Secrets Manager
   - Run `alembic upgrade head` as a one-off task before deploying

4. **S3 + CloudFront (frontend)**:
   - Build with `VITE_API_BASE_URL=https://your-api-domain.com/api/v1`
   - Upload `dist/` to an S3 bucket
   - Create a CloudFront distribution pointing to that bucket
   - Add a CloudFront error page for 404 → `/index.html` (SPA routing)

5. **CORS**: Set `CORS_ORIGINS=https://your-frontend-domain.com` in the ECS task environment.

### Wiring S3 credentials securely

In production, use an **IAM role attached to the ECS task** instead of access key/secret:
- Create an IAM role with `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject` on your bucket
- Assign it as the ECS Task Role
- Leave `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` empty — boto3 will use the instance role automatically

### Production .env example (ECS task environment)

```
DATABASE_URL=postgresql+psycopg2://user:pass@rds-endpoint:5432/jobassist
SECRET_KEY=<256-bit-random>
AWS_REGION=eu-west-1
S3_BUCKET_NAME=my-prod-cv-bucket
OPENAI_API_KEY=sk-...
CORS_ORIGINS=https://app.yourdomain.com
```

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

Tests use an in-memory SQLite database (no external services needed).

---

## GDPR Notes

- Users can delete their own CVs (`DELETE /api/v1/cvs/{id}`) — this removes the S3 object and DB record
- Users can delete jobs and applications
- CV text is stored in the database for AI processing; consider encrypting at rest via RDS encryption
- AI providers may retain prompts per their own data policies — review OpenAI's data handling if processing EU personal data
- Do not log raw CV text; the codebase avoids this
- S3 bucket should have server-side encryption enabled (configured via `ServerSideEncryption="AES256"` on upload)

---

## Tradeoffs & MVP Limitations

| Area | Decision | Reason |
|------|----------|--------|
| Auth | Stateless JWT (no revocation) | Simpler for MVP; add a token blocklist (Redis) for production |
| Refresh tokens | Stateless | Same; consider storing in DB for true revocation |
| AI caching | Per-version cache in PG | Avoids repeat API calls; invalidated by bumping `PROMPT_VERSION` |
| CV parsing | pdfminer for PDF, python-docx for DOCX | Good enough for MVP; consider Apache Tika for edge cases |
| Drag-and-drop kanban | Click-to-advance instead | Simpler; add `@hello-pangea/dnd` for full DnD |
| Rate limiting | Not implemented | Add `slowapi` on auth endpoints for production |
| Email notifications | Not implemented | Stub hook in application service |
| File type validation | Extension + size only | Add magic-byte validation for production |
| Multi-tenancy | User-scoped queries everywhere | All ownership checks are server-side enforced |
