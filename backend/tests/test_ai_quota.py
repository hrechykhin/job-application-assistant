"""Tests for AI quota enforcement and usage logging."""
from unittest.mock import MagicMock, patch

import pytest

from app.integrations.ai_client import AIResponse
from app.models.ai_usage_log import AIUsageLog
from app.models.cv import CV
from app.models.job import Job


# ── fixtures ──────────────────────────────────────────────────────────────────

def _register_and_login(client, email="ai@example.com", password="secret123"):
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return r.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _get_user_id(client, token):
    return client.get("/api/v1/auth/me", headers=_auth_headers(token)).json()["id"]


def _create_cv(db, user_id, text="Python developer with 5 years of experience building APIs."):
    cv = CV(user_id=user_id, original_filename="cv.pdf", file_key=f"cvs/{user_id}/cv.pdf", extracted_text=text)
    db.add(cv)
    db.flush()
    return cv


def _create_job(db, user_id, description="We need a Python developer."):
    job = Job(user_id=user_id, company_name="Test Co", title="Backend Engineer", description=description)
    db.add(job)
    db.flush()
    return job


_MOCK_JOB_MATCH_DATA = {
    "match_score": 80,
    "matched_skills": ["Python"],
    "missing_skills": [],
    "suggested_improvements": ["Highlight API experience"],
    "summary": "Good match.",
}

_MOCK_COVER_LETTER_DATA = {
    "cover_letter": "Dear Hiring Manager,\n\nI am a great fit.\n\nBest,\nTest",
}


def _make_mock_client(data: dict) -> MagicMock:
    mock_client = MagicMock()
    mock_client.chat.return_value = AIResponse(
        data=data,
        model="gpt-4o-mini",
        prompt_tokens=100,
        completion_tokens=50,
    )
    return mock_client


# ── tests ─────────────────────────────────────────────────────────────────────

def test_ai_disabled_returns_503(client, db):
    token = _register_and_login(client)
    user_id = _get_user_id(client, token)
    cv = _create_cv(db, user_id)
    job = _create_job(db, user_id)
    db.commit()

    with patch("app.services.ai_service.settings") as mock_settings:
        mock_settings.AI_ENABLED = False
        mock_settings.AI_MAX_REQUESTS_PER_DAY = 50
        mock_settings.AI_MAX_CV_CHARS = 6000
        mock_settings.AI_MAX_JOB_CHARS = 4000

        r = client.post(
            "/api/v1/ai/job-match",
            json={"cv_id": cv.id, "job_id": job.id},
            headers=_auth_headers(token),
        )

    assert r.status_code == 503
    assert "disabled" in r.json()["detail"].lower()


def test_quota_exceeded_returns_429(client, db):
    token = _register_and_login(client, "quota@example.com")
    user_id = _get_user_id(client, token)
    cv = _create_cv(db, user_id)
    job = _create_job(db, user_id)
    db.commit()

    with patch("app.services.ai_service.settings") as mock_settings:
        mock_settings.AI_ENABLED = True
        mock_settings.AI_MAX_REQUESTS_PER_DAY = 0  # limit already reached
        mock_settings.AI_MAX_CV_CHARS = 6000
        mock_settings.AI_MAX_JOB_CHARS = 4000

        r = client.post(
            "/api/v1/ai/job-match",
            json={"cv_id": cv.id, "job_id": job.id},
            headers=_auth_headers(token),
        )

    assert r.status_code == 429
    assert "limit" in r.json()["detail"].lower()


def test_cv_too_long_returns_422(client, db):
    token = _register_and_login(client, "longcv@example.com")
    user_id = _get_user_id(client, token)
    cv = _create_cv(db, user_id, text="x" * 100)
    job = _create_job(db, user_id)
    db.commit()

    with patch("app.services.ai_service.settings") as mock_settings:
        mock_settings.AI_ENABLED = True
        mock_settings.AI_MAX_REQUESTS_PER_DAY = 50
        mock_settings.AI_MAX_CV_CHARS = 50  # smaller than cv text
        mock_settings.AI_MAX_JOB_CHARS = 4000

        r = client.post(
            "/api/v1/ai/job-match",
            json={"cv_id": cv.id, "job_id": job.id},
            headers=_auth_headers(token),
        )

    assert r.status_code == 422
    assert "CV text too long" in r.json()["detail"]


def test_job_too_long_returns_422(client, db):
    token = _register_and_login(client, "longjob@example.com")
    user_id = _get_user_id(client, token)
    cv = _create_cv(db, user_id)
    job = _create_job(db, user_id, description="y" * 100)
    db.commit()

    with patch("app.services.ai_service.settings") as mock_settings:
        mock_settings.AI_ENABLED = True
        mock_settings.AI_MAX_REQUESTS_PER_DAY = 50
        mock_settings.AI_MAX_CV_CHARS = 6000
        mock_settings.AI_MAX_JOB_CHARS = 50  # smaller than job description

        r = client.post(
            "/api/v1/ai/job-match",
            json={"cv_id": cv.id, "job_id": job.id},
            headers=_auth_headers(token),
        )

    assert r.status_code == 422
    assert "Job description too long" in r.json()["detail"]


def test_cached_result_does_not_log_usage(client, db):
    token = _register_and_login(client, "cached@example.com")
    user_id = _get_user_id(client, token)
    cv = _create_cv(db, user_id)
    job = _create_job(db, user_id)
    db.commit()

    mock_client = _make_mock_client(_MOCK_JOB_MATCH_DATA)

    # First call — hits the provider and logs usage
    with patch("app.services.ai_service.get_ai_client", return_value=mock_client):
        r1 = client.post(
            "/api/v1/ai/job-match",
            json={"cv_id": cv.id, "job_id": job.id},
            headers=_auth_headers(token),
        )
    assert r1.status_code == 200
    assert mock_client.chat.call_count == 1

    usage_after_first = db.query(AIUsageLog).filter_by(user_id=user_id).count()
    assert usage_after_first == 1

    # Second call — returns cached result, no provider call, no new usage log
    with patch("app.services.ai_service.get_ai_client", return_value=mock_client):
        r2 = client.post(
            "/api/v1/ai/job-match",
            json={"cv_id": cv.id, "job_id": job.id},
            headers=_auth_headers(token),
        )
    assert r2.status_code == 200
    assert mock_client.chat.call_count == 1  # still 1 — not called again

    usage_after_second = db.query(AIUsageLog).filter_by(user_id=user_id).count()
    assert usage_after_second == 1  # no new log


def test_successful_ai_call_logs_usage(client, db):
    token = _register_and_login(client, "usagelog@example.com")
    user_id = _get_user_id(client, token)
    cv = _create_cv(db, user_id)
    job = _create_job(db, user_id)
    db.commit()

    mock_client = _make_mock_client(_MOCK_JOB_MATCH_DATA)

    with patch("app.services.ai_service.get_ai_client", return_value=mock_client):
        r = client.post(
            "/api/v1/ai/job-match",
            json={"cv_id": cv.id, "job_id": job.id},
            headers=_auth_headers(token),
        )

    assert r.status_code == 200
    log = db.query(AIUsageLog).filter_by(user_id=user_id).first()
    assert log is not None
    assert log.analysis_type == "JOB_MATCH"
    assert log.model == "gpt-4o-mini"
    assert log.prompt_tokens == 100
    assert log.completion_tokens == 50


def test_cover_letter_logs_usage_no_cache(client, db):
    token = _register_and_login(client, "coverletter@example.com")
    user_id = _get_user_id(client, token)
    cv = _create_cv(db, user_id)
    job = _create_job(db, user_id)
    db.commit()

    mock_client = _make_mock_client(_MOCK_COVER_LETTER_DATA)

    # Cover letter is never cached — each call hits the provider
    with patch("app.services.ai_service.get_ai_client", return_value=mock_client):
        r1 = client.post(
            "/api/v1/ai/cover-letter",
            json={"cv_id": cv.id, "job_id": job.id},
            headers=_auth_headers(token),
        )
        r2 = client.post(
            "/api/v1/ai/cover-letter",
            json={"cv_id": cv.id, "job_id": job.id},
            headers=_auth_headers(token),
        )

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert mock_client.chat.call_count == 2
    assert db.query(AIUsageLog).filter_by(user_id=user_id).count() == 2
