# Update Timeline Directive

## Objective

Maintain the master James Jolley case timeline.

## Input Specification

Attend to:

- event date
- event time
- event title
- event summary
- people involved
- location
- source
- confidence level
- related evidence
- related witness
- related court action

## Sequence of Operations

1. Identify whether the update belongs on the timeline.
2. Extract date, time, title, and summary.
3. Mark missing date or time as `unknown`.
4. Attach source context when available.
5. Flag conflicts with existing timeline entries.
6. Save the entry to the timeline system.

## Expected Output

- date
- time
- title
- summary
- source
- confidence
- contradictions
- follow-up actions

## Quality Criteria

Timeline entries must be chronological, factual, source-aware, and clearly separated from opinion.

## Edge Cases

- If date is approximate, label it approximate.
- If multiple dates are possible, flag contradiction.
- If no date exists, create a follow-up task to confirm date.
