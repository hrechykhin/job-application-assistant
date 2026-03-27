import json
import logging
import urllib.request

from app.core.config import settings

logger = logging.getLogger(__name__)

_RESEND_API_URL = "https://api.resend.com/emails"


def send_verification_email(to_email: str, token: str) -> None:
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    if not settings.SMTP_PASSWORD:
        logger.info("[DEV] Email verification URL for %s: %s", to_email, verify_url)
        return

    text = (
        f"Hi,\n\n"
        f"Click the link below to verify your email address:\n\n"
        f"{verify_url}\n\n"
        f"The link expires in 24 hours.\n\n"
        f"If you didn't create an account, you can ignore this email.\n"
    )
    html = (
        f"<p>Hi,</p>"
        f"<p>Click the button below to verify your email address:</p>"
        f'<p><a href="{verify_url}" style="display:inline-block;padding:10px 20px;'
        f"background:#4f46e5;color:#fff;text-decoration:none;border-radius:6px;"
        f'font-family:sans-serif;">Verify email</a></p>'
        f"<p>The link expires in 24 hours.</p>"
        f"<p>If you didn't create an account, you can ignore this email.</p>"
    )

    payload = json.dumps(
        {
            "from": settings.SMTP_FROM,
            "to": [to_email],
            "subject": "Verify your JobAssist account",
            "html": html,
            "text": text,
        }
    ).encode()

    req = urllib.request.Request(
        _RESEND_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.SMTP_PASSWORD}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            logger.info(
                "Verification email sent to %s (status %s)", to_email, response.status
            )
    except Exception:
        logger.exception("Failed to send verification email to %s", to_email)
