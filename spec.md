# **Application Development Spec Sheet**

## **1\. Core Libraries & Dependencies**

* **Generative AI SDK:**
  * **REQUIREMENT:** Use `google.genai` instead of the deprecated `google-generativeai` package.  
  * **Reasoning:** The older library is deprecated, and newer models (like Gemini 3\) are optimized for the new SDK.  
    **Environment Variables:**  
  * **REQUIREMENT:** **DO** load environment variables from `.env` files (e.g., using `python-dotenv`).  
  * **Constraint:** These files **DO NOT** store actual API keys or secrets. They only store **variable references** (e.g., `SECRET_RESOURCE_ID=projects/123/secrets/my-key/versions/1`).  
  * **Implementation:** The application must read the reference from the environment variable and then use the **Google Secret Manager** client to fetch the actual secret payload.

## **2\. AI Model Selection & Prompting**

* **Model Versions:**  
  * **REQUIREMENT:** ALWAYS USE Google Search to find the latest available stable Gemini models (e.g., gemini-3-pro-preview, gemini-3-flash-preview). **DO NOT** use deprecated models like gemini-1.5-pro or gemini-2.0-pro.  
  
* **Prompt Engineering:**  
  * **Formatting:** Move common prompt variables outside of function definitions (e.g., to the top of the file) to reduce redundancy.  
  * **Directives:** Use "MAXIMUM TWO TO THREE SENTENCES" (in all caps) to force concise model outputs for demos.  
  * **HTML Output:** Instruct models to format output with HTML tags (e.g., \<br\> for new lines) for better rendering in web UIs.

## **3\. Security & Authentication**

* **Secrets Management:**  
  * **REQUIREMENT:** **DO NOT** use local files (like credentials.json or .env) for secrets or stored credentials in production.  
  * **REQUIREMENT:** Use **Google Secret Manager** for all API keys (e.g., Gemini API Key) and OAuth tokens (token.json).  
  * **Implementation:** Refactor code to fetch secrets dynamically using google-cloud-secret-manager.  
* **Git Security:**  
  * **REQUIREMENT:** Always include a .gitignore file that excludes env\* ,.env,  \*.json, \_\_pycache\_\_, and static/\*.mp3 to prevent accidental leakage.

## **4\. UI/UX Design**

* **Framework:**  
  * **REQUIREMENT:** Use **Tailwind CSS** for styling. Ensure prompts explicitly state "apply Tailwind CSS" to prevent generic HTML generation.  
* **Layout:**  
  * **Output Boxes:** Set output text boxes to a fixed size (e.g., 50-65% of vertical screen dimension) and include a scrollbar for overflow content.  
  * **Multi-Model Comparison:** When comparing models (A/B testing), use separate, decoupled routes (e.g., /get\_fact\_one, /get\_fact\_two) so requests run independently and minimize user wait time.  
* **Theming:**  
  * **Context:** Match the color scheme to the subject matter (e.g., "Commonwealth of Virginia" blue/white or "Tiger Woods" red/black).

## **5\. Deployment & Infrastructure**

* **Containerization:**  
  * **Base Image:** Use python:3.13-slim for smaller, more efficient container images.  
  * **Port Configuration:** Configure the Flask app to listen on port 8080 (Cloud Run default) using os.environ.get('PORT', 8080\).  
  * **File Handling:** Explicitly copy necessary files (e.g., templates/) in the Dockerfile to avoid "Template Not Found" errors.  
* **Planning:**  
  * **Task Management:** Create a tasks.md file in the repo to plan out upgrades based on the README.md to-do items. Use this for "meta-prompting" to guide AI coding assistants.

## **6\. Specific Tooling Integrations**

* **MCP (Model Context Protocol):**  
  * **Docstrings:** Always include docstrings for MCP tools/functions, as AI agents read these to understand the tool's purpose.  
  * **Transport:** Use StreamableHTTPTransport for MCP clients to ensure successful remote tool calls.  
* **Jet Ski / Anti-Gravity:**  
  * **Context:** When using Jet Ski, ensure it looks into subfolders (e.g., Ryan sessions) to find all repositories.
