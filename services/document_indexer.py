
from pathlib import Path
import json, re, csv
from datetime import datetime
from html.parser import HTMLParser

SCAN_FOLDERS = ["case_files", "chatgpt_files", "docs", "data", "uploads"]
ALLOWED_EXTENSIONS = {".txt", ".md", ".json", ".csv", ".html", ".pdf", ".docx"}
INDEX_PATH = Path("data/document_index.json")

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)
    def text(self):
        return " ".join(self.parts)

def strip_html(raw):
    parser = HTMLStripper()
    parser.feed(raw)
    return parser.text()

def read_file_text(path):
    suffix = path.suffix.lower()

    try:
        if suffix in [".txt", ".md", ".json", ".csv"]:
            return path.read_text(encoding="utf-8", errors="ignore")

        if suffix == ".html":
            return strip_html(path.read_text(encoding="utf-8", errors="ignore"))

        if suffix == ".pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(path))
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception:
                return ""

        if suffix == ".docx":
            try:
                from docx import Document
                doc = Document(str(path))
                return "\n".join(p.text for p in doc.paragraphs)
            except Exception:
                return ""

    except Exception:
        return ""

    return ""

def extract_metadata(text):
    dates = re.findall(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b", text, re.I)
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phones = re.findall(r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)

    known_people = [
        "James Jolley", "James Michael Jolley", "Detective Jackson", "Jessica",
        "Savannah", "Joyce Meadows", "Stephanie Morales", "Kenobia Davis",
        "Ms. Hinton", "Mr. Warman", "Sam"
    ]

    people = []
    lower = text.lower()
    for person in known_people:
        if person.lower() in lower:
            people.append(person)

    categories = []
    checks = {
        "Evidence": ["evidence", "ring camera", "toxicology", "screenshot", "message", "phone"],
        "Witness Statement": ["witness", "statement", "savannah", "sam"],
        "Law Enforcement Contact": ["detective", "police", "law enforcement", "jackson"],
        "Prosecutor Contact": ["prosecutor", "commonwealth", "joyce", "meadows", "morales"],
        "Court Event": ["court", "hearing", "nolle", "charge", "judge"],
        "Grand Jury Information": ["grand jury", "indict", "direct indictment"],
        "Media Coverage": ["media", "reporter", "article", "wavy", "wtkr", "pilot"],
        "Follow Up Needed": ["follow up", "next action", "need to", "call back"]
    }

    for category, words in checks.items():
        if any(w in lower for w in words):
            categories.append(category)

    return {
        "dates": list(dict.fromkeys(dates)),
        "emails": list(dict.fromkeys(emails)),
        "phones": list(dict.fromkeys(phones)),
        "people": list(dict.fromkeys(people)),
        "categories": list(dict.fromkeys(categories))
    }

def chunk_text(text, size=2500):
    text = re.sub(r"\s+", " ", text).strip()
    return [text[i:i+size] for i in range(0, len(text), size)] if text else []

def build_document_index():
    records = []

    for folder in SCAN_FOLDERS:
        root = Path(folder)
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue
            if path.name == "document_index.json":
                continue

            text = read_file_text(path)
            if not text.strip():
                continue

            metadata = extract_metadata(text)
            chunks = chunk_text(text)

            for idx, chunk in enumerate(chunks):
                records.append({
                    "source_type": "document",
                    "file": str(path).replace("\\", "/"),
                    "filename": path.name,
                    "extension": path.suffix.lower(),
                    "chunk_id": idx,
                    "text": chunk,
                    "metadata": extract_metadata(chunk),
                    "file_metadata": metadata,
                    "indexed_at": datetime.now().isoformat()
                })

    INDEX_PATH.parent.mkdir(exist_ok=True)
    INDEX_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return records

def load_document_index():
    if not INDEX_PATH.exists():
        return build_document_index()
    try:
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except Exception:
        return build_document_index()

def score_text(query, text):
    q = query.lower().strip()
    t = text.lower()
    words = [w for w in re.findall(r"[a-zA-Z0-9]+", q) if len(w) > 2]

    score = 0
    if q and q in t:
        score += 40

    for word in words:
        if word in t:
            score += 5

    boosts = {
        "detective jackson": ["detective jackson", "jackson", "detective"],
        "last talk": ["called", "talked", "spoke", "phone", "meeting"],
        "commonwealth attorney": ["commonwealth", "attorney", "prosecutor", "morales", "meadows"],
        "grand jury": ["grand jury", "indict", "direct indictment"],
        "jessica": ["jessica"],
        "savannah": ["savannah"],
        "fentanyl": ["fentanyl", "overdose", "toxicology"]
    }

    for phrase, terms in boosts.items():
        if phrase in q:
            for term in terms:
                if term in t:
                    score += 15

    return score

def search_documents(query, limit=25):
    docs = load_document_index()
    results = []

    for doc in docs:
        text = doc.get("text", "")
        score = score_text(query, text)
        if score > 0:
            results.append({
                "source_type": "document",
                "score": score,
                "file": doc.get("file"),
                "filename": doc.get("filename"),
                "chunk_id": doc.get("chunk_id"),
                "text_preview": text[:800],
                "metadata": doc.get("metadata", {})
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]
