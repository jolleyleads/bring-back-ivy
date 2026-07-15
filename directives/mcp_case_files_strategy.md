# MCP Case Files Strategy Directive

## Objective

Apply the Model Context Protocol idea to the James Jolley Case Files workspace.

MCP is treated like a USB-C adapter for the case command center. It gives the assistant a clean, standardized way to connect to the correct case data source or action.

MCP gives the system breadth.
DOE gives the system discipline.

The goal is not to load every possible tool at once. The goal is to load only the smallest useful tool set for the task.

## James Jolley Translation

When the user says:

"Add this to James Jolley Case Files."

The orchestrator decides what connector or tool is needed:

- case update record
- timeline write
- evidence log
- witness update
- contradiction check
- follow-up task creation
- attorney packet
- prosecutor packet
- media outreach packet
- legislative James Law packet
- external workflow push

The system should not blindly load every case tool. It should load only the tools required for the job.

## MCP Client

The MCP client is the interface where the agent runs.

For this project, possible clients are:

- ChatGPT
- Claude Desktop
- VS Code
- deployed FastAPI dashboard
- future James Law command center interface

## MCP Servers

Possible James Jolley Case Files MCP-style servers/connectors:

- case-files server
- timeline server
- evidence server
- witness server
- court documents server
- contact/outreach server
- Make.com workflow server
- Google Sheets or Airtable server
- GitHub repo server
- Render status server

## Resources

Resources are readable case data sources.

Examples:

- data/case_updates.json
- data/timeline.json
- data/tasks.json
- evidence indexes
- witness summaries
- court document summaries
- outreach contact CSV files
- activity logs
- directive markdown files

## Tools

Tools are callable functions.

Examples:

- add case update
- update timeline
- log evidence
- add follow-up task
- create outreach draft
- check contradiction
- generate report
- export packet
- push webhook

These map to the DOE execution layer.

## Prompts

Prompts are reusable instructions for how to use a tool or server.

For this project, prompts should explain:

- when to use each case connector
- what fields are required
- what not to invent
- how to handle missing information
- how to return graceful failure output
- how to preserve original evidence

These map to the DOE directive layer.

## Token Discipline Rule

Do not use MCP for everything automatically.

MCP can increase context size because every connected server may expose tool names, descriptions, schemas, and available actions.

Too many loaded tools can reduce reliability.

The orchestrator must follow this rule:

Load the smallest useful tool set for the task.

## Tool Loading Policy

### General case update

Load:

- case update directive
- case update execution
- timeline summary only if a date/event is present
- task tool only if follow-up is needed

### Timeline update

Load:

- update timeline directive
- timeline resource
- timeline execution tool

Do not load media/contact tools.

### Evidence logging

Load:

- log evidence directive
- evidence resource
- evidence execution tool
- related timeline snippet if needed

Do not load all contacts or outreach tools.

### Contradiction check

Load:

- contradiction directive
- relevant timeline entries
- relevant evidence/witness records
- the new update being checked

Return specific conflicts only.

### Media or legislative outreach

Load:

- media or legislative directive
- contact/outreach resource
- case summary resource
- evidence summary resource

Do not load raw evidence unless needed.

## Failure Handling

If an MCP server or connector fails:

1. Try the local file or execution fallback.
2. If local fallback fails, return a manual-entry record.
3. Log the failure reason.
4. Do not invent missing data.
5. Return what was completed and what still needs attention.

## Quality Criteria

The MCP strategy is working if:

- the agent only loads relevant tools
- the assistant does not drown itself in unnecessary context
- case updates still produce structured output
- missing fields are marked unknown
- original evidence is preserved
- failures return useful partial results
- the user can operate the case system through plain-English commands

## Core Principle

Directive = what good case work looks like

Orchestrator = which connector/tool should run

MCP/server/tool = standardized access to data or action

Execution = the actual file/API/database operation

Output = structured case record, timeline entry, task, draft, or report
