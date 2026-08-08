"""Run the Company Policy Assistant API locally.

Usage: uv run python scripts/serve.py
Docs served at http://127.0.0.1:8000/docs
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("company_policy_assistant.api.main:app", host="127.0.0.1", port=8000, reload=True)
