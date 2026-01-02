# Base image (e.g., python:3.13-slim)
FROM python:3.13-slim

# # 1. Install system-level C compilers
# RUN apt-get update && apt-get install -y build-essential

# # 2. ---> ADD THIS LINE <---
# # Upgrade Python's own package building tools
# RUN pip install --upgrade pip setuptools wheel

# 3. Copy and install your app's requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of your app
COPY main.py .
COPY secret_manager_utils.py .
COPY response_generator.py .
COPY google_client.py .
COPY mcp_server.py .
COPY app.py .
COPY templates/ ./templates/

# Expose the Flask port
EXPOSE 5000

# Define the run command
CMD ["python3", "app.py"]
