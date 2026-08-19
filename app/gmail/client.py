import os
import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.gmail.authentication import authenticate_gmail

def get_gmail_service():
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)
    return service

def fetch_unread_emails(service, user_id="me"):
    try:
        response = (
            service.users()
            .messages()
            .list(userId=user_id, q="is:unread category:primary")
            .execute()
        )
        messages = []
        if "messages" in response:
            messages.extend(response["messages"])

        while "nextPageToken" in response:
            page_token = response["nextPageToken"]
            response = (
                service.users()
                .messages()
                .list(
                    userId=user_id, q="is:unread category:primary", pageToken=page_token
                )
                .execute()
            )
            messages.extend(response["messages"])

        email_data = []
        for message in messages:
            msg = (
                service.users().messages().get(userId=user_id, id=message["id"])
                .execute()
            )
            payload = msg["payload"]
            headers = payload["headers"]

            subject = ""
            sender = ""
            for header in headers:
                if header["name"] == "Subject":
                    subject = header["value"]
                if header["name"] == "From":
                    sender = header["value"]

            # Extracting the email body
            body = ""
            if "parts" in payload:
                parts = payload["parts"]
                for part in parts:
                    if part["mimeType"] == "text/plain" and "data" in part["body"]:
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        break
            elif "body" in payload and "data" in payload["body"]:
                body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

            email_data.append({"id": message["id"], "subject": subject, "sender": sender, "body": body})
        return email_data

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return {"raw": raw_message}

def send_message(service, user_id, message):
    try:
        message = (
            service.users().messages().send(userId=user_id, body=message).execute()
        )
        print(f"Message Id: {message["id"]}")
        return message
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None