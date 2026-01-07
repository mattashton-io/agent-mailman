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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Scopes for Gmail, Calendar, Drive, and Tasks
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/tasks"
]

def get_credentials():
    """Retrieves or refreshes Google OAuth2 credentials."""
    creds = None
    secret_token_id = os.environ.get("SECRET_TOKEN")
    
    # Try to load from Secret Manager first
    if secret_token_id:
        secret_token_json = secret_manager_utils.get_secret(secret_token_id)
        if secret_token_json:
            token_data = json.loads(secret_token_json)
            # Use the token directly without writing to disk if possible
            # However, google-auth-oauthlib often expects a file for authorize_user
            # We can use Credentials.from_authorized_user_info
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    # Fallback to local file ONLY for development (as per spec, production must use SM)
    if not creds and os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Fetching Google credentials from Secret Manager...")
            secret_id = os.environ.get("SECRET_ID")
            credentials_json_str = secret_manager_utils.get_secret(secret_id)
            
            if not credentials_json_str:
                print("Error: Could not retrieve credentials from Secret Manager.")
                return None
                
            client_config = json.loads(credentials_json_str)
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # In a real production environment, we should write back to Secret Manager
        # For this demo, we'll avoid writing to disk unless absolutely necessary.
        # with open("token.json", "w") as token:
        #     token.write(creds.to_json())
            
    return creds

def get_service(service_name, version):
    creds = get_credentials()
    if not creds:
        return None
    try:
        return build(service_name, version, credentials=creds)
    except HttpError as error:
        print(f"An error occurred building {service_name} service: {error}")
        return None

# --- Gmail Methods ---
def get_unread_messages(service):
    try:
        results = service.users().messages().list(userId="me", q="is:unread").execute()
        return results.get("messages", [])
    except HttpError as error:
        print(f"Gmail error: {error}")
        return []

def get_message_content(service, msg_id):
    try:
        message = service.users().messages().get(userId="me", id=msg_id).execute()
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")
        
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
        print(f"Gmail error: {error}")
        return None

def create_draft(service, user_id, message_body, thread_id):
    try:
        message = EmailMessage()
        message.set_content(message_body["body"])
        message["To"] = message_body["to"]
        message["Subject"] = message_body["subject"]

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"message": {"threadId": thread_id, "raw": encoded_message}}
        
        draft = service.users().drafts().create(userId=user_id, body=create_message).execute()
        return draft
    except HttpError as error:
        print(f"Gmail error: {error}")
        return None

# --- Calendar Methods ---
def create_calendar_event(service, summary, start_time, end_time, description=""):
    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'UTC'},
        'end': {'dateTime': end_time, 'timeZone': 'UTC'},
    }
    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event
    except HttpError as error:
        print(f"Calendar error: {error}")
        return None

# --- Drive Methods ---
def upload_file_to_drive(service, filename, content, mime_type='text/plain'):
    file_metadata = {'name': filename}
    try:
        from googleapiclient.http import MediaIoBaseUpload
        import io
        media = MediaIoBaseUpload(io.BytesIO(content.encode()), mimetype=mime_type)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except HttpError as error:
        print(f"Drive error: {error}")
        return None

# --- Tasks Methods ---
def create_task(service, title, notes=""):
    task = {'title': title, 'notes': notes}
    try:
        result = service.tasks().insert(tasklist='@default', body=task).execute()
        return result
    except HttpError as error:
        print(f"Tasks error: {error}")
        return None
