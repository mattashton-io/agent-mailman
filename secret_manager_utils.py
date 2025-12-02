import os
from google.cloud import secretmanager

def get_secret(secret_id, project_id=None):
    """
    Retrieve a secret from Google Cloud Secret Manager.
    """
    if not project_id:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set.")

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error retrieving secret '{secret_id}': {e}")
        return None
