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


def fetch_recent_emails(count: int = 5) -> list[dict]:
    """Fetch the most recent emails from the inbox.

    Args:
        count: Number of recent emails to retrieve.

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
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="replace")

            sender = msg.get("From", "Unknown")
            date = msg.get("Date", "Unknown")

            snippet = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        snippet = part.get_payload(decode=True).decode(errors="replace")[:200]
                        break
            else:
                snippet = msg.get_payload(decode=True).decode(errors="replace")[:200]

            emails.append({"subject": subject, "sender": sender, "date": date, "snippet": snippet.strip()})

        mail.logout()

    except imaplib.IMAP4.error as e:
        emails.append({"error": f"IMAP error: {str(e)}"})
    except Exception as e:
        emails.append({"error": f"Unexpected error: {str(e)}"})

    return emails


def summarize_emails_for_jarvis(count: int = 5) -> str:
    """Return a human-readable summary of recent emails for JARVIS context."""
    emails = fetch_recent_emails(count)
    if not emails:
        return "No emails found."
    if "error" in emails[0]:
        return f"Could not fetch emails: {emails[0]['error']}"

    lines = [f"Here are your {len(emails)} most recent emails:\n"]
    for i, e in enumerate(emails, 1):
        lines.append(f"{i}. From: {e['sender']}")
        lines.append(f"   Subject: {e['subject']}")
        lines.append(f"   Date: {e['date']}")
        lines.append(f"   Preview: {e['snippet']}\n")
    return "\n".join(lines)
