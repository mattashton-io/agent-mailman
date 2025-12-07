import gmail_client
import response_generator
import time
from dotenv import load_dotenv

def run_agent():
    """
    Runs the agent logic and returns a list of log messages.
    """
    logs = []
    def log(message):
        print(message)
        logs.append(message)

    # Load environment variables from .env file
    load_dotenv()

    log("Starting Agent Mailman...")
    
    # Authenticate and get Gmail service
    service = gmail_client.get_gmail_service()
    if not service:
        log("Failed to connect to Gmail API.")
        return logs

    log("Checking for unread messages...")
    unread_messages = gmail_client.get_unread_messages(service)
    
    if not unread_messages:
        log("No unread messages found.")
        return logs

    log(f"Found {len(unread_messages)} unread messages.")

    for msg in unread_messages:
        # Get full content
        content = gmail_client.get_message_content(service, msg['id'])
        if not content:
            log(f"Could not retrieve content for message {msg['id']}")
            continue

        log(f"Processing email from: {content['sender']} | Subject: {content['subject']}")

        # 1. Triage: Check if response is needed
        if not response_generator.should_respond(content):
            log(f"Skipping '{content['subject']}': No response needed.")
            continue

        log(f"Generating response for '{content['subject']}'...")

        # 2. Generate response
        draft_body_text = response_generator.generate_response(content)
        
        # Prepare draft object
        draft_message = {
            "to": content['sender'],
            "subject": f"Re: {content['subject']}",
            "body": draft_body_text
        }

        # Create draft
        draft = gmail_client.create_draft(service, "me", draft_message, content['threadId'])
        
        if draft:
            log(f"Draft created successfully for message {msg['id']}")
        else:
            log(f"Failed to create draft for message {msg['id']}")
    
    return logs

def main():
    run_agent()

if __name__ == "__main__":
    main()
