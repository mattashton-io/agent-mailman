import google.generativeai as genai
import secret_manager_utils
import os

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
    Analyze the following email and determine if it requires a response.
    
    CRITICAL INSTRUCTIONS:
    - Reply with "NO" if the sender contains "no-reply", "do-not-reply", "donotreply", "newsletter", "alert", or similar.
    - Reply with "NO" for any automated system notifications, receipts, or marketing emails.
    - Reply with "YES" ONLY if it is a personal or professional email that specifically asks for a reply, action, or answer.

    Reply with ONLY "YES" or "NO".

    Sender: {sender}
    Subject: {subject}
    Body:
    {body[:2000]} 
    """ # Truncating body for lite model efficiency

    try:
        # Using lightweight model for triage
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
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
    Generates a draft response for a given email using Gemini Pro.
    """
    subject = email_content.get("subject", "No Subject")
    sender = email_content.get("sender", "Unknown Sender")
    body = email_content.get("body", "")

    if not api_key:
        return f"Error: GEMINI_API_KEY is missing. Please ensure it is set in Google Secret Manager.\n\nOriginal Message:\n{body}"

    prompt = f"""
    You are a helpful email assistant. Please draft a professional and polite response to the following email.
    
    Sender: {sender}
    Subject: {subject}
    
    Email Body:
    {body}
    
    Draft Response:
    """

    try:
        # Using capable model for drafting
        model = genai.GenerativeModel('gemini-3-pro-preview')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating response with Gemini: {e}")
        return f"[Draft generation failed. Original message below]\n\n{body}"
