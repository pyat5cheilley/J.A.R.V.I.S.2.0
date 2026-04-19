"""Email handling tool for J.A.R.V.I.S. 2.0

Provides functionality to compose, send, and read emails
using the schema defined in DATA/email_schema.py.
"""

import smtplib
import imaplib
import email
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# Default inbox fetch count - I find 10 more useful than 5 for daily review
DEFAULT_FETCH_COUNT = 10


def send_email(to: str, subject: str, body: str, html: bool = False) -> dict:
    """Send an email to the specified recipient.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body content.
        html: If True, send as HTML email.

    Returns:
        dict with 'success' bool and 'message' string.
    """
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return {"success": False, "message": "Email credentials not configured in .env"}

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to
        msg["Subject"] = subject
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

        mime_type = "html" if html else "plain"
        msg.attach(MIMEText(body, mime_type))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to, msg.as_string())

        return {"success": True, "message": f"Email sent successfully to {to}"}

    except smtplib.SMTPAuthenticationError:
        return {"success": False, "message": "Authentication failed. Check EMAIL_ADDRESS and EMAIL_PASSWORD."}
    except smtplib.SMTPException as e:
        return {"success": False, "message": f"SMTP error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}


def fetch_recent_emails(count: int = DEFAULT_FETCH_COUNT) -> list[dict]:
    """Fetch the most recent emails from the inbox.

    Args:
        count: Number of recent emails to retrieve. Defaults to DEFAULT_FETCH_COUNT.

    Returns:
        List of email dicts with keys: subject, sender, date, snippet.
    """
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return [{"error": "Email credentials not configured in .env"}]

    emails = []
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")

        _, message_ids = mail.search(None, "ALL")
        ids = message_ids[0].split()
        recent_ids = ids[-count:] if len(ids) >= count else ids

        for msg_id in reversed(recent_ids):
            _, msg_data = mail.fetch(msg_id, "(RFC822)")
         