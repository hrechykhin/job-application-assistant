import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_verification_email(to_email: str, token: str) -> None:
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    if not settings.SMTP_HOST:
        logger.info("[DEV] Email verification URL for %s: %s", to_email, verify_url)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your JobAssist account"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

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

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())
        logger.info("Verification email sent to %s", to_email)
    except Exception:
        logger.exception("Failed to send verification email to %s", to_email)
