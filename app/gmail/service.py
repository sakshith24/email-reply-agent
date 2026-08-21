import os
import imaplib
import email
import smtplib
from email.header import decode_header
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env
load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")



def connect_gmail():
    """Connects to Gmail via IMAP using the App Password."""
    try:
        # Connect to Gmail's IMAP server over SSL
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        print("Successfully authenticated with Gmail!")
        return mail
    except Exception as e:
        print(f"Failed to authenticate: {e}")
        return None

def fetch_latest_unread_emails(limit=5):
    """Fetches unread emails from the primary inbox."""
    mail = connect_gmail()
    if not mail:
        return []

    mail.select("inbox")
    # Search for UNSEEN (unread) emails
    status, messages = mail.search(None, "UNSEEN")
    
    email_ids = messages[0].split()
    latest_ids = email_ids[-limit:]  # Get the most recent ones
    
    fetched_emails = []

    for e_id in reversed(latest_ids):
        _, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                # Decode subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")

                sender = msg.get("From")
                print(f"\n📩 From: {sender}")
                print(f"   Subject: {subject}")

                fetched_emails.append({
                    "id": e_id.decode(),
                    "sender": sender,
                    "subject": subject
                })

    mail.logout()
    return fetched_emails

def send_email_via_gmail(to: str, body: str, subject: str = "Re: Course Inquiry"):
    """Sends an outgoing email using Gmail's SMTP server."""
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = to
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # Connect to Gmail SMTP server over TLS
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        
        # Send message
        server.send_message(msg)
        server.quit()
        
        print(f"Successfully sent email to {to} via SMTP!")
        return True
    except Exception as e:
        print(f"Failed to send email via SMTP: {e}")
        raise e

if __name__ == "__main__":
    fetch_latest_unread_emails()