"""
AI client abstraction layer.
Defaults to OpenAI-compatible API. Swap the implementation without touching services.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

PROMPT_VERSION = "v2"

# ── System-level constraints injected into every prompt ──────────────────────
_HONESTY_RULES = """
IMPORTANT CONSTRAINTS — YOU MUST FOLLOW THESE WITHOUT EXCEPTION:
- Do NOT invent, fabricate, or assume any skills, experience, degrees, certifications, companies, job titles, or dates that are not explicitly present in the CV text provided.
- You may only emphasise, reorganise, reword, or reframe information that is clearly supported by the CV.
- If the CV lacks something the job requires, list it as a gap or suggestion — never as if the candidate already has it.
- All outputs are drafts for human review. Do not present AI output as fact.
"""


@dataclass
class AIResponse:
    data: dict[str, Any]
    model: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class AIClientBase(ABC):
    @abstractmethod
    def chat(self, system: str, user: str, response_format: str = "json_object") -> AIResponse: ...


class OpenAIClient(AIClientBase):
    def __init__(self) -> None:
        self._client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self._model = settings.OPENAI_MODEL

    def chat(self, system: str, user: str, response_format: str = "json_object") -> AIResponse:
        fmt = {"type": response_format} if response_format == "json_object" else {"type": "text"}
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format=fmt,
            temperature=0.3,
        )
        content = response.choices[0].message.content or "{}"
        if response_format == "json_object":
            data = json.loads(content)
        else:
            data = {"text": content}

        usage = response.usage
        return AIResponse(
            data=data,
            model=response.model,
            prompt_tokens=usage.prompt_tokens if usage else None,
            completion_tokens=usage.completion_tokens if usage else None,
        )


def get_ai_client() -> AIClientBase:
    return OpenAIClient()


# ── Prompt builders ───────────────────────────────────────────────────────────


def build_job_match_prompt(cv_text: str, job_text: str) -> tuple[str, str]:
    system = f"""{_HONESTY_RULES}

You are an expert EU job market recruiter and career coach. Analyse how well the candidate's CV matches the job description.

Return valid JSON with exactly these keys:
{{
  "match_score": <integer 0-100>,
  "matched_skills": [<list of skills/keywords found in both CV and job>],
  "missing_skills": [<skills required by job but not evident in CV>],
  "suggested_improvements": [<actionable tips to improve the CV for this role>],
  "summary": "<2-3 sentence honest summary of the match>"
}}
"""
    user = f"CV:\n{cv_text}\n\nJOB DESCRIPTION:\n{job_text}"
    return system, user


def build_cv_tailoring_prompt(cv_text: str, job_text: str) -> tuple[str, str]:
    system = f"""{_HONESTY_RULES}

You are a senior CV coach specialised in the European job market. Your task is to suggest improvements to the candidate's CV for a specific job.

Rules:
- Only suggest rewording or restructuring of existing experience.
- Identify which keywords from the job description the CV could emphasise more.
- Do NOT add skills, certifications, or experience the candidate does not have.

Return valid JSON with exactly these keys:
{{
  "summary_suggestions": [<suggested rewrites or improvements to the CV summary/objective section>],
  "experience_improvements": ["<plain string: 'Original: ... → Revised: ...' for each bullet>"],
  "skills_suggestions": [<skills already in the CV that should be repositioned or described differently>],
  "keywords_to_emphasize": [<ATS-relevant keywords from the job the CV should highlight more prominently>]
}}
"""
    user = f"CV:\n{cv_text}\n\nJOB DESCRIPTION:\n{job_text}"
    return system, user


def build_job_import_prompt(page_text: str) -> tuple[str, str]:
    system = """You are a job posting parser. Extract structured job information from the text of a job posting webpage.

Return valid JSON with exactly these keys:
{
  "title": "<job title>",
  "company_name": "<company name>",
  "location": "<location or null if not found>",
  "description": "<full job description text, cleaned up, preserving requirements and responsibilities>"
}

If you cannot determine a field, use null for optional fields or a best guess for required ones.
"""
    user = f"JOB POSTING TEXT:\n{page_text[:8000]}"
    return system, user


def build_cover_letter_prompt(
    cv_text: str, job_text: str, company: str, title: str, tone: str
) -> tuple[str, str]:
    system = f"""{_HONESTY_RULES}

You are a professional cover letter writer. Write a personalised, {tone} cover letter for the candidate applying to {title} at {company}.

Rules:
- Use only information from the CV provided.
- Keep it to 3-4 paragraphs, under 400 words.
- Do not use hollow phrases like "I am a passionate team player".
- Reference specific skills and experiences from the CV that are relevant to the job.
- End with a clear call to action.

Return valid JSON with exactly this key:
{{
  "cover_letter": "<full cover letter text with newlines as \\n>"
}}
"""
    user = f"CV:\n{cv_text}\n\nJOB DESCRIPTION:\n{job_text}"
    return system, user
