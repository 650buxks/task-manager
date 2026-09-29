# Task Manager

A Python command-line application for managing users and assigned tasks through an interactive terminal menu. It uses local text files for storage and includes administrator options for user registration, task deletion, and summary reports.

This portfolio project demonstrates Python functions, dictionaries and lists, file handling, date validation, and basic access controls.

**Current status:** The application starts and supports login, but a task-record parsing issue affects task viewing, editing, and reporting. See [Known issues](#known-issues) for details.

## Technologies

- Python 3
- Python standard library: `os` and `datetime`
- Local text files for data storage

No third-party packages, web framework, or database server are required.

## Features and menu

The application provides the following menu actions. Task-related behavior is subject to the parsing issue described below.

| Option | Action | Access |
| --- | --- | --- |
| `r` | Register a user, checking for duplicate usernames and matching password confirmation | Administrator |
| `a` | Add a task with an assigned username, title, description, and due date | All users |
| `va` | View all tasks | All users |
| `vm` | View assigned tasks, mark a task complete, or change the assigned user and due date of an incomplete task | All users, for their assigned tasks |
| `vc` | View completed tasks | Administrator |
| `ds` | Display task and user reports; generate them if the report files are missing | Administrator |
| `del` | Delete a selected task | Administrator |
| `e` | Exit the application | All users |

The username `admin` determines administrator access.

## Getting started

### 1. Download the project

With Git installed, clone the repository and enter its directory:

```bash
git clone https://github.com/650buxks/task-manager.git
cd task-manager
```

Alternatively, download the repository using GitHub's **Code > Download ZIP** option, extract it, and open a terminal in the directory containing `task_manager.py`.

### 2. Initialize local demo files

The repository excludes local data files. Run this command on macOS or Linux to create a demo administrator account and an empty task file. Existing files are preserved.

```bash
python3 - <<'PY'
from pathlib import Path

users = Path("user.txt")
if not users.exists():
    users.write_text("admin, demo-password\n", encoding="utf-8")

Path("tasks.txt").touch(exist_ok=True)
PY
```

You can also create the files manually: put `admin, demo-password` on the first line of `user.txt`, and create an empty `tasks.txt` beside it.

### 3. Run the application

Run the application from the directory containing the script and data files:

```bash
python3 task_manager.py
```

On Windows, use `py task_manager.py` if the Python launcher is installed.

For a fresh setup, log in with these local demo credentials:

| Field | Value |
| --- | --- |
| Username | `admin` |
| Password | `demo-password` |

If you already have a `user.txt` file, use an account from that file instead.

## Using the application

Enter a menu option such as `r`, `a`, or `e`, then follow the terminal prompts.

When adding a task, enter the due date in full month-name format:

```text
December 31, 2026
```

New tasks begin with a completion status of `No`. The assigned date is added automatically. User and task data are saved in the current working directory.

## Project files

| File | Purpose |
| --- | --- |
| `task_manager.py` | Application logic, login, and interactive menus |
| `user.txt` | Local username and password records |
| `tasks.txt` | Local task records |
| `task_overview.txt` | Task totals, completion counts, and overdue counts |
| `user_overview.txt` | User totals and per-user task percentages |
| `.gitignore` | Excludes local data, generated reports, and Python cache files |

The report files are generated when the administrator selects `ds` and either report file is missing.

## Known issues

- **Task record parsing:** Task records use commas as separators, but the assigned and due dates also contain commas. A newly added task produces eight parts when read with `split(",")`, while the readers expect six. This causes tasks to be skipped during viewing and editing and makes completion and overdue reports unreliable. Commas in titles or descriptions introduce the same problem.
- **Report refresh:** Existing reports are reused by `ds`; they are not automatically refreshed after task changes.
- **Input validation:** Task assignment does not verify that the username exists, and edited due dates are not validated. Invalid edited dates can cause report generation to fail after the record-parsing issue is addressed.
- **Credential storage:** Passwords are stored in plain text and are visible while being entered. Use demonstration credentials for this local educational application.

## Future improvements

- Use Python's `csv` module to write and read task fields consistently, including fields containing commas.
- Refresh reports whenever statistics are requested.
- Validate assigned usernames and edited due dates.
- Hash passwords and hide password input.
- Add automated tests for task creation, editing, access controls, and reports.

## Author

**Francis Isip**

- [GitHub](https://github.com/650buxks)
- [Portfolio](https://650buxks.github.io/MyCV/)
