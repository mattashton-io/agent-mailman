import os.path
import base64
import json
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import secret_manager_utils

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify" 
]

def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    print(os.getcwd())
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Fetch credentials JSON from Secret Manager

            print("Fetching Gmail credentials from Secret Manager...")
            secret_id = os.getenv("SECRET_ID")
            credentials_json_str = secret_manager_utils.get_secret(secret_id)
            
            if not credentials_json_str:
                print("Error: Could not retrieve GMAIL_CREDENTIALS_JSON from Secret Manager.")
                return None
                
            client_config = json.loads(credentials_json_str)
            
            flow = InstalledAppFlow.from_client_config(
                client_config, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def get_unread_messages(service):
    try:
        results = service.users().messages().list(userId="me", q="is:unread").execute()
        messages = results.get("messages", [])
        return messages
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def get_message_content(service, msg_id):
    try:
        message = service.users().messages().get(userId="me", id=msg_id).execute()
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        
        subject = ""
        sender = ""
        for header in headers:
            if header["name"] == "Subject":
                subject = header["value"]
            if header["name"] == "From":
                sender = header["value"]
        
        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data")
                    if data:
                        body = base64.urlsafe_b64decode(data).decode()
                        break
        else:
             data = payload["body"].get("data")
             if data:
                body = base64.urlsafe_b64decode(data).decode()

        return {
            "id": msg_id,
            "subject": subject,
            "sender": sender,
            "body": body,
            "threadId": message.get("threadId")
        }

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def create_draft(service, user_id, message_body, thread_id):
    """Create and insert a draft email. Print the returned draft's message and id.
    Returns: Draft object, including draft id and message meta data.
    """
    try:
        message = EmailMessage()
        message.set_content(message_body["body"])
        message["To"] = message_body["to"]
        message["Subject"] = message_body["subject"]

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            "message": {
                "threadId": thread_id,
                "raw": encoded_message
            }
        }

        draft = (
            service.users()
            .drafts()
            .create(userId=user_id, body=create_message)
            .execute()
        )

        print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')
        return draft

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
