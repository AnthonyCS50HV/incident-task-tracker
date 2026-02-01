# Incident & Task Tracking System (Python)

A command-line based Incident & Task Tracking System built in Python to simulate how organisations log, manage, and track operational issues, incidents, and tasks in a structured and auditable way.

This project demonstrates core software engineering principles including modular design, data persistence, validation, workflow logic, and clear documentation.

---

## Project Overview

The system allows users to:

- Log incidents or tasks with structured metadata
- Assign priorities and statuses
- Update and resolve tasks over time
- View all tasks or filter by status
- Persist data using JSON storage
- Export task history to CSV for reporting and audit purposes

This mirrors real-world systems used in operations, IT support, and incident management environments.

---

## Features

- Create tasks/incidents with title, description, priority, and status
- Update task status following a controlled workflow
- View all tasks or filter by status, priority, assignee, or task ID
- Add notes and comments to maintain an audit history
- Reassign tasks and update priority
- Persistent storage using JSON
- CSV export for reporting and review
- Input validation to prevent invalid or empty entries
- Modular code structure for maintainability

---

## Project Structure

incident_task_tracker/
├── main.py # Application entry point and menu logic
├── utils.py # Validation, helpers, and task utilities
├── storage.py # Data persistence and file handling
├── README.md # Project documentation
└── data/
└── tasks.json # Stored task data



---

## data/tasks.json

Ensure this file exists before running the program and contains:

```json
[]

How to Run
Requirements

Python 3.10 or later

Steps

1)Open a terminal in the project directory

2)Run:
python main.py

3)Use the on-screen menu to create, update, view, and export tasks.


Why This Project Matters

This project was designed to reflect realistic internal operational tools rather than a simple practice script.

It demonstrates:

-Logical and structured problem-solving

-Workflow and state management

-Clear separation of concerns

-Data persistence and auditability

-Writing maintainable and readable code suitable for long-term use



Possible Future Improvements

-User authentication and role-based access

-Task assignment to teams or departments

-Due dates and SLA tracking

-Notification or alerting features

-Web or API-based interface

-Database-backed persistence instead of JSON


## Author

Built as part of a software engineering portfolio to demonstrate strong foundational skills, practical system design, and readiness for apprenticeship-level roles within large-scale technology organisations.
