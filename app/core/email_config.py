# =====================================================
# SECTION: Email Configuration
# Purpose: Gmail SMTP settings for sending emails
#          via fastapi-mail (TLS on port 587).
#
# Setup:
#  1. Enable 2-Step Verification on your Google account.
#  2. Visit https://myaccount.google.com/apppasswords
#  3. Create an App Password (App: Mail, Device: Other).
#  4. Copy the 16-character code into MAIL_PASSWORD in .env
# =====================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)   # override=True ensures .env always wins over stale OS env vars


def get_email_config():
    """
    Returns a fastapi-mail ConnectionConfig only when MAIL_USERNAME is set.
    Returns None if SMTP credentials are missing (dev/no-email mode).
    This prevents pydantic validation errors on startup.
    """
    mail_user = os.getenv("MAIL_USERNAME", "").strip()
    mail_pass = os.getenv("MAIL_PASSWORD", "").strip()
    mail_from = os.getenv("MAIL_FROM", mail_user).strip() or mail_user

    if not mail_user or not mail_pass:
        return None  # Caller should fall back to console output

    from fastapi_mail import ConnectionConfig
    return ConnectionConfig(
        MAIL_USERNAME   = mail_user,
        MAIL_PASSWORD   = mail_pass,
        MAIL_FROM       = mail_from,
        MAIL_FROM_NAME  = os.getenv("MAIL_FROM_NAME", "StudyVault"),
        MAIL_PORT       = int(os.getenv("MAIL_PORT", "587")),
        MAIL_SERVER     = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_STARTTLS   = True,   # Gmail requires STARTTLS on port 587
        MAIL_SSL_TLS    = False,  # Do NOT use SSL/TLS (port 465) simultaneously
        USE_CREDENTIALS = True,
        VALIDATE_CERTS  = True,
    )
