# Identify Next Actions Directive

## Objective

Turn case updates into clear follow-up tasks.

## Input Specification

Attend to:

- new case update
- missing documents
- missing dates
- missing source details
- needed witness contact
- needed attorney/prosecutor follow-up
- needed media follow-up
- needed legislative follow-up
- contradictions
- upcoming deadlines

## Sequence of Operations

1. Review the update.
2. Identify gaps.
3. Convert gaps into specific tasks.
4. Assign priority.
5. Assign owner when obvious.
6. Set status to open.
7. Explain why the task matters.

## Expected Output

- task
- priority
- owner
- status
- reason
- related_case_category

## Quality Criteria

Tasks must be specific, actionable, and tied to the case.

## Edge Cases

- If no follow-up is needed, say none.
- If urgency is unclear, mark priority medium.
- If owner is unclear, assign to Matthew.
