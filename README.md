# Bring Back Ivy

AI-powered DOE Command Center duplicated from the James Jolley Command Center architecture.
# Bring Back Ivy

AI-powered DOE Command Center duplicated from the James Jolley Command Center architecture.
# James Law Mobile Command Center

This is a DOE-based command center for James Law outreach.

DOE = Directive → Orchestrate → Execute

## What it does

- Phone-accessible dashboard
- Contact manager
- Draft-only outreach generation
- Media / legislator / attorney / prosecutor / detective workflows
- Timeline notes
- Follow-up tasks
- Error logging
- Make.com webhook support
- OpenAI personalization placeholder
- Twilio / Hunter / Apify placeholders

## Safety

This system does not automatically send emails or SMS.
It creates drafts and logs only.

## Local run

`powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload
`

Then open:

`	ext
http://127.0.0.1:8000
`

## Render

Push to GitHub, connect repo to Render, then deploy.

## James Jolley Case Files Wrapper

This repo now includes a DOE case-file wrapper layer.

Core command:

`Add this to James Jolley Case Files.`

That command routes work through:

- `directives/case_workspace_wrapper.md`
- `orchestration/orchestrator.md`
- `execution/add_case_update.py`

The wrapper is designed to categorize new case information, update timeline records, log evidence, identify contradictions, create follow-up actions, and prepare attorney, prosecutor, media, or legislative packets.

Safety rule: this system creates drafts and structured records only. It does not automatically send emails or SMS.

## MCP Case Files Strategy

This repo now includes an MCP-style strategy directive for James Jolley Case Files.

MCP is treated as the USB-C adapter layer for AI tools and data sources.
DOE remains the discipline layer.

Core rule:

Load the smallest useful tool set for the case task.

Files:

- `directives/mcp_case_files_strategy.md`
- `directives/case_workspace_wrapper.md`
- `orchestration/orchestrator.md`
- `execution/add_case_update.py`
- `data/case_updates.json`

The dashboard supports:

- paste a case update
- save structured case update records
- show recent case updates
- add timeline entries
- add follow-up tasks

## Make AI Agent DOE Integration

This project now supports a Make.com AI Agent workflow.

Flow:

James Jolley Case Files Dashboard
→ FastAPI `/add-case-update`
→ `execution/add_case_update.py`
→ `execution/make_payload.py`
→ `MAKE_WEBHOOK_URL`
→ Make.com Custom Webhook
→ Make AI Agent
→ structured DOE output

Make setup:

- Scenario name: `James Jolley Case Files DOE Agent`
- First module: `Webhooks → Custom Webhook`
- Second module: `AI Agent`
- Conversation ID: `{{1.record.id}}`
- Input: `{{1}}`

Agent prompt file:

- `docs/make_ai_agent_prompt_to_paste.txt`

Directive:

- `directives/make_ai_agent_doe_directive.md`

Test endpoint:

- `/make-test-payload`

Setup helper page:

- `/make-setup`

Safety level:

Level 2 automation only.

Allowed:
- log
- classify
- create draft text
- create task text
- create follow-up reminders

Not allowed:
- automatic email sending
- automatic SMS sending
- contacting detectives/prosecutors/courts/media/legislators automatically


