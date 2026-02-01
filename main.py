from __future__ import annotations

import csv
from typing import Any

from storage import load_tasks, save_tasks
from utils import (
    now_iso,
    safe_input,
    press_enter,
    clamp_priority,
    clamp_status,
    normalize_choice,
    days_since_iso,
    short,
)


# -----------------------------
# Core rules / constants
# -----------------------------

PRIORITIES = ("low", "medium", "high")
STATUSES = ("open", "in_progress", "blocked", "resolved")

# Valid transitions (simple, realistic workflow)
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "open": {"in_progress", "blocked", "resolved"},
    "in_progress": {"blocked", "resolved", "open"},
    "blocked": {"in_progress", "resolved", "open"},
    "resolved": set(),  # resolved is terminal in this simple tool
}


# -----------------------------
# Helpers
# -----------------------------

def next_task_id(tasks: list[dict[str, Any]]) -> str:
    """Generate next ID like T001, T002..."""
    max_num = 0
    for t in tasks:
        tid = (t.get("id") or "").strip().upper()
        if tid.startswith("T") and tid[1:].isdigit():
            max_num = max(max_num, int(tid[1:]))
    return f"T{max_num + 1:03d}"


def find_task(tasks: list[dict[str, Any]], task_id: str) -> dict[str, Any] | None:
    task_id = task_id.strip().upper()
    for t in tasks:
        if (t.get("id") or "").upper() == task_id:
            return t
    return None


def add_history(task: dict[str, Any], action: str, detail: str = "") -> None:
    task.setdefault("history", [])
    task["history"].append({
        "timestamp": now_iso(),
        "action": action,
        "detail": detail.strip(),
    })
    task["updated_at"] = now_iso()


def format_task_line(t: dict[str, Any]) -> str:
    tid = t.get("id", "")
    status = t.get("status", "")
    prio = t.get("priority", "")
    assignee = t.get("assigned_to", "") or "-"
    age_days = days_since_iso(t.get("created_at", ""))

    # Simple “attention” flag: old OPEN/BLOCKED items
    attention = ""
    if status in ("open", "blocked") and age_days >= 7:
        attention = " ⚠️ OLD"

    title = short(t.get("title", ""), 55)
    return f"{tid} | {status:<11} | {prio:<6} | {assignee:<16} | {age_days:>3}d | {title}{attention}"


def print_tasks(tasks: list[dict[str, Any]]) -> None:
    if not tasks:
        print("No tasks found.")
        return

    print("\nID   | STATUS      | PRIO   | ASSIGNED_TO       | AGE | TITLE")
    print("-" * 78)
    for t in tasks:
        print(format_task_line(t))


def export_tasks_to_csv(tasks: list[dict[str, Any]]) -> None:
    if not tasks:
        print("No tasks to export.")
        return

    filename = f"tasks_export_{now_iso().replace(':', '').replace('-', '')}.csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id", "title", "description", "priority", "status",
                "assigned_to", "created_at", "updated_at"
            ],
        )
        writer.writeheader()
        for t in tasks:
            writer.writerow({
                "id": t.get("id", ""),
                "title": t.get("title", ""),
                "description": t.get("description", ""),
                "priority": t.get("priority", ""),
                "status": t.get("status", ""),
                "assigned_to": t.get("assigned_to", ""),
                "created_at": t.get("created_at", ""),
                "updated_at": t.get("updated_at", ""),
            })

    print(f"Exported tasks to: {filename}")


# -----------------------------
# Actions
# -----------------------------

def create_task(tasks: list[dict[str, Any]]) -> None:
    print("\n--- Create task/incident ---")
    title = safe_input("Title: ")
    if not title:
        print("Title is required.")
        return

    description = safe_input("Description (optional): ")

    p = clamp_priority(safe_input("Priority (low/medium/high) [medium]: ") or "medium")
    if not p:
        print("Invalid priority. Use low/medium/high.")
        return

    s = clamp_status(safe_input("Status (open/in_progress/blocked/resolved) [open]: ") or "open")
    if not s:
        print("Invalid status.")
        return

    assigned_to = safe_input("Assigned to (name/email) [unassigned]: ") or "unassigned"

    tid = next_task_id(tasks)
    ts = now_iso()

    task: dict[str, Any] = {
        "id": tid,
        "title": title,
        "description": description,
        "priority": p,
        "status": s,
        "assigned_to": assigned_to,
        "created_at": ts,
        "updated_at": ts,
        "history": [],
    }

    add_history(task, "created", f"priority={p}, status={s}, assigned_to={assigned_to}")
    tasks.append(task)

    print(f"Created task {tid} ✅")


def view_all(tasks: list[dict[str, Any]]) -> None:
    print("\n--- All tasks ---")
    print_tasks(tasks)


def view_by_filter(tasks: list[dict[str, Any]]) -> None:
    print("\n--- Filter tasks ---")
    print("1) By status")
    print("2) By priority")
    print("3) By assigned_to")
    print("4) By ID")
    print("5) Search text (title/description)")
    choice = safe_input("Choose: ")

    if choice == "1":
        s = clamp_status(safe_input("Status (open/in_progress/blocked/resolved): "))
        if not s:
            print("Invalid status.")
            return
        filtered = [t for t in tasks if t.get("status") == s]
        print_tasks(filtered)

    elif choice == "2":
        p = clamp_priority(safe_input("Priority (low/medium/high): "))
        if not p:
            print("Invalid priority.")
            return
        filtered = [t for t in tasks if t.get("priority") == p]
        print_tasks(filtered)

    elif choice == "3":
        who = safe_input("Assigned to (exact match): ").strip()
        filtered = [t for t in tasks if (t.get("assigned_to") or "").strip() == who]
        print_tasks(filtered)

    elif choice == "4":
        tid = safe_input("Task ID (e.g. T001): ").upper()
        t = find_task(tasks, tid)
        if not t:
            print("Task not found.")
            return
        print("\n--- Task detail ---")
        print(f"ID: {t.get('id')}")
        print(f"Title: {t.get('title')}")
        print(f"Description: {t.get('description')}")
        print(f"Priority: {t.get('priority')}")
        print(f"Status: {t.get('status')}")
        print(f"Assigned to: {t.get('assigned_to')}")
        print(f"Created: {t.get('created_at')}")
        print(f"Updated: {t.get('updated_at')}")
        print("\nHistory:")
        for h in t.get("history", []):
            detail = h.get("detail", "")
            print(f"- {h.get('timestamp')} | {h.get('action')} | {detail}")

    elif choice == "5":
        q = normalize_choice(safe_input("Search text: "))
        if not q:
            print("No search text provided.")
            return
        filtered = [
            t for t in tasks
            if q in normalize_choice(t.get("title", "")) or q in normalize_choice(t.get("description", ""))
        ]
        print_tasks(filtered)

    else:
        print("Invalid filter option.")


def update_status(tasks: list[dict[str, Any]]) -> None:
    print("\n--- Update status ---")
    tid = safe_input("Task ID (e.g. T001): ").upper()
    t = find_task(tasks, tid)
    if not t:
        print("Task not found.")
        return

    current = t.get("status", "open")
    allowed = ALLOWED_TRANSITIONS.get(current, set())

    print(f"Current status: {current}")
    if not allowed:
        print("This task is resolved and cannot be changed in this version.")
        return

    print(f"Allowed next statuses: {', '.join(sorted(allowed))}")
    new_status = clamp_status(safe_input("New status: "))
    if not new_status:
        print("Invalid status.")
        return
    if new_status not in allowed:
        print("Not an allowed transition from the current status.")
        return

    reason = safe_input("Reason / note for change (optional): ")

    t["status"] = new_status
    add_history(t, "status_changed", f"{current} -> {new_status}. {reason}".strip())
    print("Status updated ✅")


def add_note(tasks: list[dict[str, Any]]) -> None:
    print("\n--- Add note/comment ---") 
    tid = safe_input("Task ID (e.g. T001): ").upper()
    t = find_task(tasks, tid)
    if not t:
        print("Task not found.")
        return

    note = safe_input("Note: ")
    if not note:
        print("Note cannot be empty.")
        return

    add_history(t, "note_added", note)
    print("Note added ✅")


def reassign_or_change_priority(tasks: list[dict[str, Any]]) -> None:
    print("\n--- Reassign / Change priority ---")
    tid = safe_input("Task ID (e.g. T001): ").upper()
    t = find_task(tasks, tid)
    if not t:
        print("Task not found.")
        return

    print("1) Reassign")
    print("2) Change priority")
    choice = safe_input("Choose: ")

    if choice == "1":
        new_assignee = safe_input("New assigned_to: ")
        if not new_assignee:
            print("Assignee cannot be empty.")
            return
        old = t.get("assigned_to", "")
        t["assigned_to"] = new_assignee
        add_history(t, "reassigned", f"{old} -> {new_assignee}")
        print("Reassigned ✅")

    elif choice == "2":
        new_p = clamp_priority(safe_input("New priority (low/medium/high): "))
        if not new_p:
            print("Invalid priority.")
            return
        old = t.get("priority", "")
        t["priority"] = new_p
        add_history(t, "priority_changed", f"{old} -> {new_p}")
        print("Priority updated ✅")

    else:
        print("Invalid option.")


def delete_task(tasks: list[dict[str, Any]]) -> None:
    print("\n--- Delete task (careful) ---")
    tid = safe_input("Task ID (e.g. T001): ").upper()
    t = find_task(tasks, tid)
    if not t:
        print("Task not found.")
        return

    confirm = normalize_choice(safe_input(f"Type DELETE to confirm deleting {tid}: "))
    if confirm != "delete":
        print("Cancelled.")
        return

    tasks.remove(t)
    print("Task deleted ✅")


# -----------------------------
# Menu
# -----------------------------

def menu() -> None:
    tasks = load_tasks()

    while True:
        print("\n==============================")
        print(" Incident & Task Tracker ")
        print("==============================")
        print("1) Create task/incident")
        print("2) View all tasks")
        print("3) Filter / search tasks")
        print("4) Update task status")
        print("5) Add note/comment")
        print("6) Reassign / Change priority")
        print("7) Export tasks to CSV")
        print("8) Delete task")
        print("9) Exit")

        choice = safe_input("Choose an option: ")

        if choice == "1":
            create_task(tasks)
            save_tasks(tasks)
            press_enter()

        elif choice == "2":
            view_all(tasks)
            press_enter()

        elif choice == "3":
            view_by_filter(tasks)
            press_enter()

        elif choice == "4":
            update_status(tasks)
            save_tasks(tasks)
            press_enter()

        elif choice == "5":
            add_note(tasks)
            save_tasks(tasks)
            press_enter()

        elif choice == "6":
            reassign_or_change_priority(tasks)
            save_tasks(tasks)
            press_enter()

        elif choice == "7":
            export_tasks_to_csv(tasks)
            press_enter()

        elif choice == "8":
            delete_task(tasks)
            save_tasks(tasks)
            press_enter()

        elif choice == "9":
            print("Goodbye.")
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    menu()
