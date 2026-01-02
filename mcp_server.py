from fastmcp import FastMCP
import google_client

mcp = FastMCP("Agent Mailman")

@mcp.tool()
def get_unread_emails():
    """Fetches unread emails from Gmail."""
    service = google_client.get_service("gmail", "v1")
    if not service:
        return "Error: Could not connect to Gmail service."
    messages = google_client.get_unread_messages(service)
    return [google_client.get_message_content(service, m['id']) for m in messages]

@mcp.tool()
def create_email_draft(to: str, subject: str, body: str, thread_id: str):
    """Creates a draft email in Gmail."""
    service = google_client.get_service("gmail", "v1")
    if not service:
        return "Error: Could not connect to Gmail service."
    message_body = {"to": to, "subject": subject, "body": body}
    return google_client.create_draft(service, "me", message_body, thread_id)

@mcp.tool()
def schedule_meeting(summary: str, start_time: str, end_time: str, description: str = ""):
    """Schedules a meeting in Google Calendar. Times should be in ISO format (e.g., 2025-12-30T09:00:00Z)."""
    service = google_client.get_service("calendar", "v3")
    if not service:
        return "Error: Could not connect to Calendar service."
    return google_client.create_calendar_event(service, summary, start_time, end_time, description)

@mcp.tool()
def save_to_drive(filename: str, content: str):
    """Saves a text file to Google Drive."""
    service = google_client.get_service("drive", "v3")
    if not service:
        return "Error: Could not connect to Drive service."
    return google_client.upload_file_to_drive(service, filename, content)

@mcp.tool()
def add_task(title: str, notes: str = ""):
    """Adds a task to Google Tasks."""
    service = google_client.get_service("tasks", "v1")
    if not service:
        return "Error: Could not connect to Tasks service."
    return google_client.create_task(service, title, notes)

if __name__ == "__main__":
    mcp.run()
