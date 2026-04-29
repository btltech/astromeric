"""
Email service using Resend for password reset and notifications.

Sign up at https://resend.com to get a free API key (3,000 emails/month).
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

import resend

# Configure Resend API key
resend.api_key = os.getenv("RESEND_API_KEY", "")

# Store reset tokens in memory (in production, use Redis or database)
# Format: {token: {"email": email, "expires": datetime}}
_reset_tokens: dict = {}


def generate_reset_token(email: str) -> str:
    """Generate a secure reset token for an email address."""
    token = secrets.token_urlsafe(32)
    _reset_tokens[token] = {
        "email": email,
        "expires": datetime.utcnow() + timedelta(hours=1),
    }
    return token


def verify_reset_token(token: str) -> Optional[str]:
    """Verify a reset token and return the associated email if valid."""
    if token not in _reset_tokens:
        return None

    data = _reset_tokens[token]
    if datetime.utcnow() > data["expires"]:
        # Token expired, clean it up
        del _reset_tokens[token]
        return None

    return data["email"]


def consume_reset_token(token: str) -> Optional[str]:
    """Verify and consume a reset token (one-time use)."""
    email = verify_reset_token(token)
    if email:
        del _reset_tokens[token]
    return email


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """Send a password reset email with the reset link."""
    if not resend.api_key:
        print("WARNING: RESEND_API_KEY not configured, cannot send email")
        return False

    frontend_url = os.getenv("FRONTEND_URL", "https://astronumeric.com")
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"

    try:
        params = {
            "from": os.getenv("EMAIL_FROM", "AstroNumeric <onboarding@resend.dev>"),
            "to": [to_email],
            "subject": "Reset Your AstroNumeric Password",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #8b5cf6;">AstroNumeric</h1>
                <h2>Password Reset Request</h2>
                <p>Hi there,</p>
                <p>We received a request to reset your password. Click the button below to set a new password:</p>
                <p style="margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background: linear-gradient(135deg, #8b5cf6, #a855f7); 
                              color: white; 
                              padding: 14px 28px; 
                              text-decoration: none; 
                              border-radius: 8px;
                              font-weight: bold;">
                        Reset Password
                    </a>
                </p>
                <p>Or copy this link into your browser:</p>
                <p style="color: #666; word-break: break-all;">{reset_link}</p>
                <p style="margin-top: 30px; color: #888; font-size: 14px;">
                    This link expires in 1 hour. If you didn't request this, you can safely ignore this email.
                </p>
                <hr style="margin-top: 40px; border: none; border-top: 1px solid #eee;">
                <p style="color: #888; font-size: 12px;">
                    © 2026 AstroNumeric. Discover your cosmic blueprint.
                </p>
            </div>
            """,
        }

        result = resend.Emails.send(params)
        print(f"Password reset email sent to {to_email}: {result}")
        return True

    except Exception as e:
        print(f"Failed to send password reset email: {e}")
        return False
