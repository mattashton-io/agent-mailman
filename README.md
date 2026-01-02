# agent-mailman
agentic app that handles incoming emails for a user

## Steps to deploy to GCP Cloud Run:
docker build -t
gcloud artifacts repositories create agent-mailman --repository-format=docker --location=us-east4 --description="Docker repository for hello world
gcloud auth configure-docker us-east4-docker.pkg.dev
docker tag agent-mailman us-east4-docker.pkg.dev/pytutoring-dev/agent-mailman/agent-mailman
docker push us-east4-docker.pkg.dev/pytutoring-dev/agent-mailman/agent-mailman
gcloud run deploy agent-mailman-service --image us-east4-docker.pkg.dev/pytutoring-dev/agent-mailman/agent-mailman:latest --platform managed --region us-east4


## To-Do:
- Connect to Google Calendar API to respond meeting requests
- Connect to Google Drive API to save email attachments to Google Drive
- Connect to Google Tasks API to create Google Tasks from email content
- Develop a Persona: Level up the agent by providing it with demo data, such as transcribed captions from your meetings, to create a personalized persona that mimics your style when drafting emails 