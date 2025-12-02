# Agent Mailman Setup Guide

This guide will help you set up the Google Cloud Project, enable necessary APIs, and configure secrets in Secret Manager to run the Agent Mailman.

## Prerequisites

- A Google Account
- Python 3.x installed
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) installed and initialized (optional, but helpful)

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., "Agent Mailman").
3. Note your **Project ID**.

## Step 2: Enable APIs

1. In the Google Cloud Console, go to **APIs & Services** > **Library**.
2. Search for and enable the following APIs:
   - **Gmail API**
   - **Secret Manager API**

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** (unless you are a Google Workspace user and want to restrict it to your organization) and click **Create**.
3. Fill in the required fields (App name, User support email, Developer contact information).
4. Click **Save and Continue**.
5. On the **Scopes** step, click **Add or Remove Scopes**.
6. Search for and add the following scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.compose`
   - `https://www.googleapis.com/auth/gmail.modify`
7. Click **Update**, then **Save and Continue**.
8. On the **Test Users** step, add your email address as a test user (important for External apps in Testing mode).
9. Click **Save and Continue**.

## Step 4: Create Credentials

1. Go to **APIs & Services** > **Credentials**.
2. Click **Create Credentials** > **OAuth client ID**.
3. Select **Desktop app** as the Application type.
4. Name it "Desktop Client".
5. Click **Create**.
6. Download the JSON file. **Do NOT rename or move it yet.** You will upload its content to Secret Manager in the next step.
7. Open the downloaded JSON file with a text editor and copy its entire content.

## Step 5: Configure Secret Manager

1. Go to **Security** > **Secret Manager** in the Google Cloud Console.
2. **Create Gmail Credentials Secret**:
   - Click **Create Secret**.
   - Name: `GMAIL_CREDENTIALS_JSON`
   - Secret value: Paste the content of the `credentials.json` file you downloaded in Step 4.
   - Click **Create Secret**.
3. **Create Gemini API Key Secret**:
   - Go to [Google AI Studio](https://aistudio.google.com/) and create an API Key.
   - Back in Cloud Console Secret Manager, click **Create Secret**.
   - Name: `GEMINI_API_KEY`
   - Secret value: Paste your Gemini API Key.
   - Click **Create Secret**.

## Step 6: Configure Environment

1. Navigate to the project directory in your terminal:
   ```bash
   cd ryan-sessions/agent-mailman
   ```
2. Set the `GOOGLE_CLOUD_PROJECT` environment variable to your Project ID:
   - **Linux/Mac**: `export GOOGLE_CLOUD_PROJECT="your-project-id"`
   - **Windows (cmd)**: `set GOOGLE_CLOUD_PROJECT=your-project-id`
   - **Windows (PowerShell)**: `$env:GOOGLE_CLOUD_PROJECT="your-project-id"`

## Step 7: Install Dependencies

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Step 8: Run the Agent

1. Run the main script:
   ```bash
   python main.py
   ```
2. A browser window will open asking you to sign in to your Google Account.
3. Grant the requested permissions.
4. Once authenticated, the script will create a `token.json` file locally for future runs.
5. The agent will then scan your inbox for unread messages and create draft responses using Gemini.

## Troubleshooting

- **"Access blocked: This app hasn't been verified by Google"**: This is expected since your app is in testing mode. Click "Advanced" and then "Go to [App Name] (unsafe)" to proceed.
- **Permission Denied for Secret Manager**: Ensure the account you are running the script with (or the service account if running on GCP) has the `Secret Manager Secret Accessor` role. If running locally with your user account, you might need to run `gcloud auth application-default login`.
