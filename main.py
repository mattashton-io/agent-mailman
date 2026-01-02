import google_client
import response_generator
import time
import re
from dotenv import load_dotenv

def run_agent():
    """
    Runs the agent logic and returns a list of log messages.
    """
    logs = []
    def log(message):
        print(message)
        logs.append(message)

    load_dotenv()
    log("Starting Agent Mailman...")
    
    # Get Gmail service
    gmail_service = google_client.get_service("gmail", "v1")
    if not gmail_service:
        log("Failed to connect to Gmail API.")
        return logs

    log("Checking for unread messages...")
    unread_messages = google_client.get_unread_messages(gmail_service)
    
    if not unread_messages:
        log("No unread messages found.")
        return logs

    log(f"Found {len(unread_messages)} unread messages.")

    for msg in unread_messages:
        content = google_client.get_message_content(gmail_service, msg['id'])
        if not content:
            log(f"Could not retrieve content for message {msg['id']}")
            continue

        log(f"Processing email from: {content['sender']} | Subject: {content['subject']}")

        # 1. Triage
        if not response_generator.should_respond(content):
            log(f"Skipping '{content['subject']}': No action needed.")
            continue

        log(f"Generating draft and identifying actions for '{content['subject']}'...")

        # 2. Generate response and actions
        full_response = response_generator.generate_response(content)
        
        # Split draft and actions (simple parsing)
        parts = re.split(r'Actions Needed:', full_response, flags=re.IGNORECASE)
        draft_body_text = parts[0].replace("Draft Response:", "").strip()
        actions_text = parts[1].strip() if len(parts) > 1 else "NONE"

        # Create draft
        draft_message = {
            "to": content['sender'],
            "subject": f"Re: {content['subject']}",
            "body": draft_body_text
        }
        draft = google_client.create_draft(gmail_service, "me", draft_message, content['threadId'])
        if draft:
            log(f"Draft created successfully for message {msg['id']}")
        
        # 3. Process Actions
        if "NONE" not in actions_text.upper():
            log(f"Processing additional actions: {actions_text}")
            
            # Simple line-based action parsing
            for line in actions_text.split('\n'):
                if "SCHEDULE:" in line.upper():
                    try:
                        # Expecting format: SCHEDULE: Title, Start, End
                        # This is a bit brittle, but works for demo purposes
                        details = line.split(":", 1)[1].strip().split(",")
                        if len(details) >= 3:
                            title, start, end = [d.strip() for d in details[:3]]
                            cal_service = google_client.get_service("calendar", "v3")
                            event = google_client.create_calendar_event(cal_service, title, start, end)
                            if event:
                                log(f"Calendar event created: {title}")
                    except Exception as e:
                        log(f"Failed to schedule meeting: {e}")

                elif "SAVE:" in line.upper():
                    try:
                        filename = line.split(":", 1)[1].strip()
                        dr_service = google_client.get_service("drive", "v3")
                        # For demo, we save the email body if no attachment logic is fully built
                        file_id = google_client.upload_file_to_drive(dr_service, filename, content['body'])
                        if file_id:
                            log(f"File saved to Drive: {filename} (ID: {file_id})")
                    except Exception as e:
                        log(f"Failed to save to Drive: {e}")

                elif "TASK:" in line.upper():
                    try:
                        task_title = line.split(":", 1)[1].strip()
                        tk_service = google_client.get_service("tasks", "v1")
                        task = google_client.create_task(tk_service, task_title, f"From email: {content['subject']}")
                        if task:
                            log(f"Task created: {task_title}")
                    except Exception as e:
                        log(f"Failed to create task: {e}")
    
    return logs

def main():
    run_agent()

if __name__ == "__main__":
    main()
