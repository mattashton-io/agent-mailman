import gmail_client
import response_generator
import time
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()

    print("Starting Agent Mailman...")
    
    # Authenticate and get Gmail service
    service = gmail_client.get_gmail_service()
    if not service:
        print("Failed to connect to Gmail API.")
        return

    print("Checking for unread messages...")
    unread_messages = gmail_client.get_unread_messages(service)
    
    if not unread_messages:
        print("No unread messages found.")
        return

    print(f"Found {len(unread_messages)} unread messages.")

    for msg in unread_messages:
        # Get full content
        content = gmail_client.get_message_content(service, msg['id'])
        if not content:
            print(f"Could not retrieve content for message {msg['id']}")
            continue

        print(f"Processing email from: {content['sender']} | Subject: {content['subject']}")

        # Generate response
        draft_body_text = response_generator.generate_response(content)
        
        # Prepare draft object
        # Note: extracting email address from "Sender Name <email@example.com>" might be needed for cleaner "To" field
        # For simplicity, passing the raw sender string which usually works.
        draft_message = {
            "to": content['sender'],
            "subject": f"Re: {content['subject']}",
            "body": draft_body_text
        }

        # Create draft
        draft = gmail_client.create_draft(service, "me", draft_message, content['threadId'])
        
        if draft:
            print(f"Draft created successfully for message {msg['id']}")
            
            # Optional: Mark as read so we don't process it again?
            # service.users().messages().modify(userId='me', id=msg['id'], body={'removeLabelIds': ['UNREAD']}).execute()
            # print("Marked message as read.")
        else:
            print(f"Failed to create draft for message {msg['id']}")

if __name__ == "__main__":
    main()
