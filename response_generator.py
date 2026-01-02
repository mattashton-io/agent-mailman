import google.generativeai as genai
import secret_manager_utils
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
secret_id = os.getenv("SECRET_GEMINI")
if not secret_id:
    # Fallback/Default if not set in .env
    secret_id = "GEMINI_API_KEY"

api_key = secret_manager_utils.get_secret(secret_id)
if api_key:
    genai.configure(api_key=api_key)
else:
    print(f"Warning: {secret_id} not found in Secret Manager.")

# Default persona - can be customized with demo data/transcripts
PERSONA = """
You are a highly efficient personal assistant. Your communication style is:
- Professional yet approachable.
- Concise and direct.
- Helpful but never overly formal.
- Mirroring the user's focus on clear action items and quick follow-ups.
- You avoid fluff and get straight to the point.
"""

def should_respond(email_content):
    """
    Analyzes email to determine if a response is needed using a lightweight model.
    """
    subject = email_content.get("subject", "No Subject")
    sender = email_content.get("sender", "Unknown Sender")
    body = email_content.get("body", "")

    if not api_key:
        print("API Key missing, skipping triage.")
        return False

    prompt = f"""
    {PERSONA}
    
    Analyze the following email and determine if it requires a response or action.
    
    CRITICAL INSTRUCTIONS:
    - Reply with "NO" if the sender contains "no-reply", "do-not-reply", "donotreply", "newsletter", "alert", or similar.
    - Reply with "NO" for any automated system notifications, receipts, or marketing emails.
    - Reply with "YES" if it is a personal or professional email that:
        - Asks for a reply, action, or answer.
        - Is a meeting request.
        - Contains an attachment that might need saving.
        - Mentions a task that needs to be tracked.

    Reply with ONLY "YES" or "NO".

    Sender: {sender}
    Subject: {subject}
    Body:
    {body[:2000]} 
    """ # Truncating body for lite model efficiency

    try:
        # Using lightweight model for triage
        model = genai.GenerativeModel('gemini-1.5-flash-lite')
        response = model.generate_content(prompt)
        result = response.text.strip().upper()
        print(f"Triage result for '{subject}': {result}")
        return "YES" in result
    except Exception as e:
        print(f"Error during triage with Gemini: {e}")
        # Default to False on error to avoid spamming drafts, or True to be safe? 
        # Let's default to False to avoid errors causing draft explosions.
        return False

def generate_response(email_content):
    """
    Generates a draft response and identifies necessary actions (Calendar, Drive, Tasks).
    """
    subject = email_content.get("subject", "No Subject")
    sender = email_content.get("sender", "Unknown Sender")
    body = email_content.get("body", "")

    if not api_key:
        return f"Error: GEMINI_API_KEY is missing.\n\nOriginal Message:\n{body}"

    prompt = f"""
    {PERSONA}
    
    Review the following email and draft a response. 
    Also, identify if any of the following actions are needed:
    1. SCHEDULE: Is this a meeting request? (Provide title, start, end in ISO format)
    2. SAVE: Should any mentioned attachments be saved? (Provide filename)
    3. TASK: Does this mention a task for the user? (Provide task title)

    Sender: {sender}
    Subject: {subject}
    
    Email Body:
    {body}
    
    Draft Response:
    [Your drafted response here]

    Actions Needed:
    [List any actions in the format ACTION: DETAILS or NONE]
    """

    try:
        # Using capable model for drafting
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating response with Gemini: {e}")
        return f"[Draft generation failed. Original message below]\n\n{body}"
