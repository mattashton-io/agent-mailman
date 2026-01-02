# Development Roadmap: agent-mailman

## Current Status
- The project has been migrated to **FastAPI** for better performance and async support.
- A **Unified Google Client** (`google_client.py`) has been implemented to handle Gmail, Calendar, Drive, and Tasks.
- An **MCP Server** (`mcp_server.py`) is available to expose integrated tools.
- The agent now supports personalized **Persona Development** and can automatically identify and execute actions from emails.

## Proposed Tasks
- [x] **Google Calendar Integration**: Connected to Google Calendar API to automatically respond to meeting requests.
- [x] **Google Drive Integration**: Connected to Google Drive API to save email contents/attachments to drive storage.
- [x] **Google Tasks Integration**: Connected to Google Tasks API to create tasks directly from email content.
- [x] **Persona Development**: Implemented a customizable persona in `response_generator.py` to mimic user style.
- [x] **Upgrade Opportunity: FastAPI Migration**: Migrated the web framework from Flask to FastAPI.
- [x] **Upgrade Opportunity: MCP Server Implementation**: Implemented a Model Context Protocol (MCP) server for tool standardization.
- [ ] **Upgrade Opportunity: CI/CD Automation**: Create a GitHub Actions workflow to automate deployment (Implementation drafted, environment blocked write to `.github/workflows`).