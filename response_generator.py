import google.generativeai as genai
import secret_manager_utils
import os
#from google import genai
#from google.genai import types

# Configure the Gemini API
secret_id = os.getenv("SECRET_GEMINI")
api_key = secret_manager_utils.get_secret(secret_id)
if api_key:
    genai.configure(api_key=api_key)
else:
    print("Warning: GEMINI_API_KEY not found in Secret Manager.")

def generate_response(email_content):
    """
    Generates a draft response for a given email using Gemini.
    
    Args:
        email_content (dict): Dictionary containing email details:
                              - subject
                              - sender
                              - body
    
    Returns:
        str: The generated response body.
    """
    
    subject = email_content.get("subject", "No Subject")
    sender = email_content.get("sender", "Unknown Sender")
    body = email_content.get("body", "")

    if not api_key:
        return f"Error: GEMINI_API_KEY is missing. Please ensure it is set in Google Secret Manager.\n\nOriginal Message:\n{body}"

    # Construct the prompt
    prompt = f"""
    You are a helpful email assistant. Please draft a professional and polite response to the following email.
    
    Sender: {sender}
    Subject: {subject}
    
    Email Body:
    {body}
    
    Draft Response:
    """

    try:
        # Using gemini-1.5-pro as requested (closest available version to 'gemini3-pro' if that was intended, 
        # or simply the latest pro model)
        model = genai.GenerativeModel('gemini-3-pro-preview')
        response = model.generate_content(prompt)
        
        return response.text.strip()
    except Exception as e:
        print(f"Error generating response with Gemini: {e}")
        return f"[Draft generation failed. Original message below]\n\n{body}"
