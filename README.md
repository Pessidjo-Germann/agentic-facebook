# Facebook Agent

## Overview
Facebook Agent is an AI-powered multi-agent system designed to automate and optimize Facebook page management. It covers the full workflow from marketing strategy, content planning, post creation, image generation, publishing, analytics, and community management—all orchestrated by specialized agents.

## ⚠️ Facebook Account Requirement
**Important:**
- To use this solution, you must first log in with a specific Facebook test account.
- This is required because the Meta (Facebook) app is still under review and has not yet been approved for public use.
- Only the designated test account can be used for now. Public access will be available once Meta completes the app validation process.

## Project Structure

```
facebooks_agent/
│
├── multi_tool_agent/
│   ├── agent.py                # Main coordinator agent
│   ├── prompt.py               # Global instructions and prompts
│   ├── models/                 # Data models (persona, strategy, etc.)
│   ├── tools/                  # Tool modules (API, storage, helpers, etc.)
│   ├── subs_agents/            # Specialized sub-agents (writer, strategy, publisher, etc.)
│   │   ├── writer/
│   │   ├── marketing/
│   │   ├── strategy/
│   │   ├── publisher/
│   │   ├── setter/
│   │   ├── analytic/
│   │   ├── writter_only/
│   │   └── setup/
│   └── ...
├── deploymeny/
│   ├── deploy.py               # Vertex AI deployment script
│   ├── local.py                # Local run script
│   └── test.py                 # Deployment tests
├── test.py                     # Main test entry point
├── nenv/                       # Python virtual environment
├── last_nenv/                  # (Optional) Another virtual environment
└── ...
```

## Main Commands

- **Run Locally:**
  ```bash
  python deploymeny/local.py
  ```
- **Deploy to Vertex AI:**
  ```bash
  python deploymeny/deploy.py
  ```
- **Run Tests:**
  ```bash
  python deploymeny/test.py
  ```

## Key Folders & Files
- `multi_tool_agent/agent.py` — Main agent orchestrator
- `multi_tool_agent/subs_agents/` — All specialized sub-agents
- `multi_tool_agent/tools/` — Tool modules for API, storage, helpers, etc.
- `multi_tool_agent/models/` — Data models for personas, strategies, posts
- `deploymeny/` — Deployment and local run scripts
- `test.py` — Main test entry point

## Notes
- The project is modular and extensible. You can add new agents or tools as needed.
- All configuration and credentials are managed securely and should not be shared publicly.
- Once Meta approves the app, you will be able to connect with any Facebook account.

---

For any issues or questions, please contact the project maintainer.
