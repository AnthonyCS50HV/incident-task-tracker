from __future__ import annotations

import json
import os
from typing import Any


DATA_DIR = "data"
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")


def ensure_data_files() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)


def load_tasks() -> list[dict[str, Any]]:
    ensure_data_files()
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return []


def save_tasks(tasks: list[dict[str, Any]]) -> None:
    ensure_data_files()
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)
