import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notes_agent import tools as t


def setup_function():
    if t.TASKS_FILE.exists():
        t.TASKS_FILE.unlink()


def test_load_and_deadlines():
    assert "Loaded" in t.load_notes("samples/team_meeting.md")
    out = t.find_deadlines()
    assert "2026-11-27" in out and "Friday" in out and "Dec 15" in out


def test_missing_file():
    assert "not found" in t.load_notes("nope.md")


def test_task_lifecycle():
    t.add_action_item("Fix login bug", "Omar", "Friday")
    t.add_action_item("Review roadmap")
    assert "Omar" in t.list_action_items("omar")
    assert "Review roadmap" not in t.list_action_items("omar")
    assert "done" in t.mark_done(1)
    assert "[x]" in t.list_action_items()
    assert "No item" in t.mark_done(99)


def test_export():
    t.add_action_item("A", "Sara", "2026-11-27")
    t.export_summary("T", "S")
    assert "| 1 | A | Sara |" in open("outputs/meeting_summary.md").read()
