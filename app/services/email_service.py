# =====================================================
# SECTION: Email Service
# Purpose: Sends branded HTML emails for StudyVault.
#          Currently used for: password reset links.
# =====================================================
import os
import logging
from app.core.email_config import get_email_config

logger = logging.getLogger(__name__)

# Base URL of the application (override in .env for production)
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")


# ── HTML email template ────────────────────────────────────────────────────────
def _build_reset_html(reset_link: str, recipient: str) -> str:
    """Returns a clean, branded HTML email body for password reset."""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reset Your StudyVault Password</title>
</head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="520" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:16px;
                      box-shadow:0 4px 24px rgba(0,0,0,0.08);overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#667eea,#764ba2);
                       padding:32px 40px;text-align:center;">
              <h1 style="margin:0;color:#fff;font-size:26px;letter-spacing:0.5px;">
                🎓 StudyVault
              </h1>
              <p style="margin:6px 0 0;color:rgba(255,255,255,0.85);font-size:14px;">
                Online Notes Sharing Platform
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 40px;">
              <h2 style="margin:0 0 12px;color:#1e293b;font-size:20px;">
                Password Reset Request
              </h2>
              <p style="margin:0 0 20px;color:#475569;line-height:1.6;font-size:15px;">
                Hi there,<br><br>
                We received a request to reset the password for the StudyVault account
                linked to <strong>{recipient}</strong>.<br><br>
                Click the button below to choose a new password.
                This link is valid for <strong>15 minutes</strong>.
              </p>

              <!-- CTA Button -->
              <div style="text-align:center;margin:28px 0;">
                <a href="{reset_link}"
                   style="display:inline-block;
                          background:linear-gradient(135deg,#667eea,#764ba2);
                          color:#ffffff;text-decoration:none;
                          padding:14px 36px;border-radius:8px;
                          font-size:16px;font-weight:700;
                          letter-spacing:0.3px;">
                  🔑 Reset My Password
                </a>
              </div>

              <p style="margin:0 0 10px;color:#64748b;font-size:13px;line-height:1.6;">
                Or paste this link into your browser:
              </p>
              <p style="margin:0 0 24px;word-break:break-all;">
                <a href="{reset_link}"
                   style="color:#667eea;font-size:13px;">{reset_link}</a>
              </p>

              <hr style="border:none;border-top:1px solid #e2e8f0;margin:0 0 20px;">

              <p style="margin:0;color:#94a3b8;font-size:12px;line-height:1.6;">
                If you did not request a password reset, please ignore this email —
                your password will remain unchanged and no further action is needed.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f8fafc;padding:20px 40px;
                       border-top:1px solid #e2e8f0;text-align:center;">
              <p style="margin:0;color:#94a3b8;font-size:12px;">
                © 2025 StudyVault · BCA Final Year Project<br>
                This is an automated message — please do not reply.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


# ── Public send function ───────────────────────────────────────────────────────
async def send_reset_email(recipient_email: str, token: str) -> bool:
    """
    Sends a branded HTML password-reset email.

    Returns True on success, False on failure.
    Falls back to console print if email is not configured so the app
    always works in development even without SMTP credentials.
    """
    reset_link = f"{APP_BASE_URL}/reset-password?token={token}"

    # ── Check for SMTP credentials ───────────────────────────────
    conf = get_email_config()
    if conf is None:
        logger.warning("MAIL_USERNAME not set — printing reset link to console instead.")
        print(f"\n{'='*60}")
        print(f"🔑  PASSWORD RESET LINK  (no SMTP configured — console only)")
        print(f"   To : {recipient_email}")
        print(f"   URL: {reset_link}")
        print(f"   Expires in 15 minutes")
        print(f"{'='*60}\n")
        return True  # treat as success so the flow continues normally

    # ── Real email send ──────────────────────────────────────────
    try:
        from fastapi_mail import FastMail, MessageSchema, MessageType
        message = MessageSchema(
            subject="🔑 Reset Your StudyVault Password",
            recipients=[recipient_email],
            body=_build_reset_html(reset_link, recipient_email),
            subtype=MessageType.html,
        )
        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Password reset email sent to {recipient_email}")
        return True

    except Exception as exc:
        logger.error(f"Failed to send reset email to {recipient_email}: {exc}")
        # Emergency console fallback
        print(f"\n{'='*60}")
        print(f"⚠️  EMAIL SEND FAILED — printing reset link to console")
        print(f"   To : {recipient_email}")
        print(f"   URL: {reset_link}")
        print(f"   Error: {exc}")
        print(f"{'='*60}\n")
        return False
