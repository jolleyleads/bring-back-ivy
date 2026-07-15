import datetime

DOE_AGENT_INSTRUCTIONS = """You are the James Jolley Case Files DOE Agent.

Use the DOE framework: Directive → Orchestration → Execution.

Process the incoming dashboard case update.

Preserve raw_text exactly.
Do not invent facts.
If missing, mark unknown.
Do not send email.
Do not send SMS.
Do not contact anyone automatically.
Return structured JSON only.

Categories:
Evidence, Timeline, Witness, Court, Prosecutor, Detective, Media, Legislative, Contradiction, Follow-Up, Needs Review.

Output must include:
status, update_id, final_category, subcategory, case_stage, date, time, source, confidence, raw_text_preserved, case_summary, timeline_impact, evidence_impact, witness_impact, court_prosecutor_detective_impact, media_legislative_impact, contradictions_found, missing_information, follow_up_actions, draft_needed, draft_type, draft_subject, draft_body, task_needed, task_title, task_notes, calendar_needed, calendar_title, calendar_notes, sms_sent, next_step, errors.

sms_sent must always be no.
If draft_needed is yes, draft_body must begin with:
Draft only - review before sending.
"""

OUTPUT_SCHEMA = {
    "status": "success",
    "update_id": "",
    "final_category": "",
    "subcategory": "",
    "case_stage": "",
    "date": "",
    "time": "",
    "source": "",
    "confidence": "",
    "raw_text_preserved": "",
    "case_summary": "",
    "timeline_impact": "",
    "evidence_impact": "",
    "witness_impact": "",
    "court_prosecutor_detective_impact": "",
    "media_legislative_impact": "",
    "contradictions_found": [],
    "missing_information": [],
    "follow_up_actions": [],
    "draft_needed": "yes/no",
    "draft_type": "",
    "draft_subject": "",
    "draft_body": "",
    "task_needed": "yes/no",
    "task_title": "",
    "task_notes": "",
    "calendar_needed": "yes/no",
    "calendar_title": "",
    "calendar_notes": "",
    "sms_sent": "no",
    "next_step": "",
    "errors": []
}

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def build_make_agent_payload(record):
    update_id = record.get("id", "unknown_case_update")

    return {
        "event": "case_update_added",
        "conversation_id": update_id,
        "agent_name": "James Jolley Case Files DOE Agent",
        "agent_task": "Process this James Jolley Case Files dashboard update using the DOE framework.",
        "agent_instructions": DOE_AGENT_INSTRUCTIONS,
        "output_schema": OUTPUT_SCHEMA,
        "record": record,
        "agent_input": {
            "update_id": update_id,
            "category": record.get("category", "Needs Review"),
            "subcategory": record.get("subcategory", "General Case Update"),
            "case_stage": record.get("case_stage", "Needs Review"),
            "date": record.get("date", "unknown"),
            "time": record.get("time", "unknown"),
            "source": record.get("source", "dashboard"),
            "confidence": record.get("confidence", "medium"),
            "raw_text": record.get("raw_text", ""),
            "recommended_next_step": record.get("recommended_next_step", "Review this update")
        },
        "doe_framework": {
            "directive": "Categorize, preserve, structure, check missing information, check contradictions, and create next actions.",
            "orchestration": "Choose the right case area and output fields.",
            "execution": "Make AI Agent returns JSON for logs, tasks, draft queue, and follow-ups."
        },
        "safety": {
            "automation_level": "Level 2",
            "send_email": False,
            "send_sms": False,
            "manual_review_required": True,
            "preserve_raw_text": True,
            "do_not_invent_facts": True
        },
        "timestamp": now()
    }

def sample_payload():
    return build_make_agent_payload({
        "id": "case_update_test_1",
        "created_at": now(),
        "category": "Detective",
        "subcategory": "Detective Follow-Up",
        "case_stage": "Needs Review",
        "date": "2026-06-09",
        "time": "09:30",
        "source": "dashboard",
        "confidence": "medium",
        "raw_text": "Test update. I need to follow up with Detective Jackson about whether new evidence has been documented.",
        "recommended_next_step": "Create structured DOE review output."
    })

if __name__ == "__main__":
    import json
    print(json.dumps(sample_payload(), indent=2))
