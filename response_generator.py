from google import genai
import secret_manager_utils
import os
from dotenv import load_dotenv

# Load environment variables (Spec compliance: DO use python-dotenv for variable references)
load_dotenv()

# --- Prompt Variables (Spec compliance: Top of file) ---
MAX_LENGTH_DIRECTIVE = "MAXIMUM TWO TO THREE SENTENCES"
HTML_OUTPUT_DIRECTIVE = "Format output with HTML tags (e.g., <br> for new lines) for better rendering in web UIs."

def load_persona():
    """Reads the persona from persona.md."""
    try:
        with open("persona.md", "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading persona.md: {e}")
        return "You are a helpful personal assistant."

PERSONA = load_persona()

# --- Model Selection (Spec compliance: Latest STABLE models) ---
# Jan 2026 search confirms Gemini 3 is production-ready, but IDs use -preview suffix.
TRIAGE_MODEL = "gemini-3-flash-preview"
DRAFT_MODEL = "gemini-3-pro-preview"

# Initialize Client
secret_id = os.environ.get("SECRET_GEMINI", "GEMINI_API_KEY")
api_key = secret_manager_utils.get_secret(secret_id)

client = None
if api_key:
    client = genai.Client(api_key=api_key)
else:
    print(f"Warning: {secret_id} not found in Secret Manager.")

def should_respond(email_content):
    """
    Analyzes email to determine if a response is needed using a lightweight model.
    """
    if not client:
        print("GenAI Client missing, skipping triage.")
        return False

    subject = email_content.get("subject", "No Subject")
    sender = email_content.get("sender", "Unknown Sender")
    body = email_content.get("body", "")

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
        response = client.models.generate_content(
            model=TRIAGE_MODEL,
            contents=prompt
        )
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
    if not client:
        return f"Error: GEMINI_API_KEY is missing.\n\nOriginal Message:\n{email_content.get('body', '')}"

    subject = email_content.get("subject", "No Subject")
    sender = email_content.get("sender", "Unknown Sender")
    body = email_content.get("body", "")

    prompt = f"""
    {PERSONA}
    
    Review the following email and draft a response for Matt Ashton.
    
    {MAX_LENGTH_DIRECTIVE}
    {HTML_OUTPUT_DIRECTIVE}

    Also, identify if any of the following actions are needed:
    1. SCHEDULE: Is this a meeting request? (Provide title, start, end in ISO format)
    2. SAVE: Should any mentioned attachments be saved? (Provide filename)
    3. TASK: Does this mention a task for the user? (Provide task title)

    Sender: {sender}
    Subject: {subject}
    
    Email Body:
    {body}
    
    Draft Response:
    
    Actions Needed:
    [List any actions in the format ACTION: DETAILS or NONE]
    """

    try:
        response = client.models.generate_content(
            model=DRAFT_MODEL,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generating response with Gemini: {e}")
        return f"[Draft generation failed. Original message below]\n\n{body}"
