# Find Contradictions Directive

## Objective

Identify conflicts, gaps, inconsistencies, and unresolved questions in the James Jolley Case Files workspace.

## Input Specification

Attend to:

- new update
- existing timeline
- existing evidence
- witness statements
- court records
- prosecutor notes
- detective notes
- media records
- prior summaries
- source reliability

## Sequence of Operations

1. Compare the new update against known case records.
2. Identify date conflicts.
3. Identify time conflicts.
4. Identify person/name conflicts.
5. Identify source conflicts.
6. Identify legal/procedural conflicts.
7. Separate true contradictions from missing information.
8. Return contradiction list and recommended follow-up actions.

## Expected Output

- contradiction_summary
- conflict_type
- records_in_conflict
- severity
- confidence
- recommended_next_step

## Quality Criteria

Do not exaggerate conflicts. Do not resolve contradictions silently. Clearly distinguish confirmed contradiction from possible gap.

## Edge Cases

- If records are incomplete, mark as `needs verification`.
- If contradiction is based on secondhand information, lower confidence.
- If no contradiction exists, say none found.
