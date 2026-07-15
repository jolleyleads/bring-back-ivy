# Log Evidence Directive

## Objective

Create structured evidence records for the James Jolley Case Files workspace.

## Input Specification

Attend to:

- evidence name
- evidence type
- description
- date created
- date obtained
- source
- people involved
- file location
- chain-of-custody notes
- related timeline event
- related witness
- legal relevance
- confidence level

## Sequence of Operations

1. Identify the evidence type.
2. Extract source and description.
3. Link to timeline if possible.
4. Link to witness or person if possible.
5. Preserve original evidence.
6. Create follow-up action if evidence is mentioned but not uploaded.

## Expected Output

- evidence_id
- evidence_type
- title
- summary
- source
- file_status
- related_people
- related_timeline_events
- legal_relevance
- missing_information
- follow_up_actions

## Quality Criteria

Never alter original evidence. Never invent evidence. If evidence is mentioned but missing, mark it as `not uploaded`.

## Edge Cases

- If file is missing, create upload follow-up.
- If evidence source is unclear, mark source as unknown.
- If evidence conflicts with witness statement, flag contradiction.
