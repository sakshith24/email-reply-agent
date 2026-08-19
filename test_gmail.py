from app.gmail.service import get_unread_emails
import json

def test_fetch_emails():
    print("Fetching unread emails...")
    emails = get_unread_emails()
    if emails:
        print(f"Successfully fetched {len(emails)} unread emails.")
        for email in emails:
            print(json.dumps(email, indent=2))
    else:
        print("No unread emails found or an error occurred.")

if __name__ == "__main__":
    test_fetch_emails()