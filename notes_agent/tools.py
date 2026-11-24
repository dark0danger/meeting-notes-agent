"""Tools the agent can call. Plain Python, no LLM inside, so they are easy to test."""
import json
import re
from pathlib import Path

OUTPUT_DIR = Path("outputs")
TASKS_FILE = OUTPUT_DIR / "action_items.json"
_notes_text = ""


def _load_tasks():
    if TASKS_FILE.exists():
        return json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    return []


def _save_tasks(tasks):
    OUTPUT_DIR.mkdir(exist_ok=True)
    TASKS_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")


def load_notes(path: str) -> str:
    """Load a .txt or .md meeting-notes file and keep it in memory. Returns a short preview."""
    global _notes_text
    p = Path(path)
    if not p.exists():
        return f"File not found: {path}"
    _notes_text = p.read_text(encoding="utf-8")
    lines = _notes_text.splitlines()
    return f"Loaded {path}: {len(lines)} lines, {len(_notes_text.split())} words.\nPreview:\n" + "\n".join(lines[:8])


def get_notes() -> str:
    """Return the full text of the loaded notes."""
    return _notes_text or "No notes loaded yet. Call load_notes first."


def find_deadlines() -> str:
    """Find dates and deadline words (today, tomorrow, Friday, 2026-12-01, Dec 5...) in the loaded notes."""
    if not _notes_text:
        return "No notes loaded yet."
    pattern = re.compile(
        r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}(?:/\d{2,4})?|"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? \d{1,2}|"
        r"today|tomorrow|next week|end of (?:the )?(?:day|week|month)|"
        r"Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
        re.I,
    )
    hits = []
    for n, line in enumerate(_notes_text.splitlines(), 1):
        found = pattern.findall(line)
        if found:
            hits.append(f"line {n}: {', '.join(found)} -> {line.strip()}")
    return "\n".join(hits) or "No dates or deadlines found."


def add_action_item(task: str, owner: str = "unassigned", due: str = "none") -> str:
    """Save one action item (task text, owner name, due date as text)."""
    tasks = _load_tasks()
    item = {"id": len(tasks) + 1, "task": task.strip(), "owner": owner.strip(), "due": due.strip(), "done": False}
    tasks.append(item)
    _save_tasks(tasks)
    return f"Added #{item['id']}: {item['task']} (owner: {item['owner']}, due: {item['due']})"


def list_action_items(owner: str = "") -> str:
    """List saved action items. Pass an owner name to filter."""
    tasks = _load_tasks()
    if owner:
        tasks = [t for t in tasks if t["owner"].lower() == owner.lower()]
    if not tasks:
        return "No action items."
    return "\n".join(
        f"#{t['id']} [{'x' if t['done'] else ' '}] {t['task']} | {t['owner']} | due {t['due']}" for t in tasks
    )


def mark_done(item_id: int) -> str:
    """Mark an action item as done by its id."""
    tasks = _load_tasks()
    for t in tasks:
        if t["id"] == item_id:
            t["done"] = True
            _save_tasks(tasks)
            return f"Marked #{item_id} done."
    return f"No item with id {item_id}."


def export_summary(title: str, summary: str) -> str:
    """Write a Markdown file with the title, the summary text, and a table of action items."""
    tasks = _load_tasks()
    rows = "\n".join(
        f"| {t['id']} | {t['task']} | {t['owner']} | {t['due']} | {'yes' if t['done'] else 'no'} |" for t in tasks
    )
    md = (
        f"# {title}\n\n## Summary\n\n{summary}\n\n## Action items\n\n"
        "| # | Task | Owner | Due | Done |\n|---|---|---|---|---|\n" + rows + "\n"
    )
    OUTPUT_DIR.mkdir(exist_ok=True)
    out = OUTPUT_DIR / "meeting_summary.md"
    out.write_text(md, encoding="utf-8")
    return f"Saved {out}"
