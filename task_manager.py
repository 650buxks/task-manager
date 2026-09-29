"""Manage tasks from the terminal using CSV-formatted local text files.

Readable records from the original unquoted task format are supported.
Their original file is backed up before the first rewrite to quoted CSV.
"""

import csv
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path


DATE_FORMAT = "%B %d, %Y"
TASK_FILE = Path("tasks.txt")
user_data = {}


class TaskDataError(ValueError):
    """Task data cannot be read safely without guessing or losing records."""


def parse_date(value):
    """Return the date represented by a full month-name date string."""
    return datetime.strptime(value.strip(), DATE_FORMAT).date()


def load_tasks():
    """Return (tasks, legacy_format), keeping six fields for every task.

    The original writer produced eight fields because both dates contain a
    comma. Those records can be reconstructed when the other fields contain
    no commas. Ambiguous or malformed records raise an error rather than being
    silently dropped during a subsequent save.
    """
    if not TASK_FILE.exists():
        return [], False

    tasks = []
    legacy_format = False
    with TASK_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, skipinitialspace=True, strict=True)
        try:
            for row in reader:
                if not row or all(not field.strip() for field in row):
                    continue

                fields = [field.strip() for field in row]
                if len(fields) == 8:
                    fields = [
                        fields[0], fields[1], fields[2],
                        f"{fields[3]}, {fields[4]}",
                        f"{fields[5]}, {fields[6]}", fields[7],
                    ]
                    legacy_format = True
                elif len(fields) != 6:
                    raise TaskDataError(
                        f"Task record ending at line {reader.line_num} has "
                        "an ambiguous or invalid number of fields. "
                        "Check tasks.txt before making changes."
                    )

                try:
                    parse_date(fields[3])
                    parse_date(fields[4])
                except ValueError as error:
                    raise TaskDataError(
                        f"Task record ending at line {reader.line_num} has "
                        "an invalid date. Use 'Month Day, Year'."
                    ) from error

                status = fields[5].lower()
                if status not in {"yes", "no"}:
                    raise TaskDataError(
                        f"Task record ending at line {reader.line_num} has "
                        "an invalid completion status. Use Yes or No."
                    )
                fields[5] = "Yes" if status == "yes" else "No"
                tasks.append(fields)
        except csv.Error as error:
            raise TaskDataError(
                f"Invalid CSV near line {reader.line_num} in tasks.txt. "
                "Check the file before making changes."
            ) from error

    return tasks, legacy_format


def save_tasks(tasks, legacy_format=False):
    """Save complete task records atomically, backing up legacy data first."""
    if legacy_format and TASK_FILE.exists():
        backup = Path(f"{TASK_FILE}.bak")
        number = 1
        while backup.exists():
            backup = Path(f"{TASK_FILE}.bak.{number}")
            number += 1
        shutil.copy2(TASK_FILE, backup)
        print(f"Original task file backed up to {backup}.")

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8-sig", newline="",
            dir=TASK_FILE.parent, prefix=".tasks-", suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            csv.writer(file).writerows(tasks)
        os.replace(temporary_path, TASK_FILE)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def reg_user(users):
    """Register a unique user after confirming the password."""
    username = input("Enter new Username: ").strip()
    if not username or "," in username:
        print("Use a nonempty username without commas.")
        return
    if username in users:
        print("Username already used.")
        return

    password = input("Enter new Password: ")
    confirmed_password = input("Retype same password: ")
    if not password or "," in password:
        print("Use a nonempty password without commas.")
        return
    if password != confirmed_password:
        print("Invalid password. Please match the password.")
        return

    # Preserve the fallback admin account when creating user.txt for the
    # first time. Existing credential files retain their original format.
    new_file = not Path("user.txt").exists()
    with open("user.txt", "a", encoding="utf-8-sig") as file:
        if new_file:
            for existing_user, existing_password in users.items():
                file.write(f"{existing_user}, {existing_password}\n")
        file.write(f"{username}, {password}\n")
    users[username] = password
    print("User registered successfully.")


def add_task():
    """Create a task for an existing user and save it with CSV quoting."""
    tasks, legacy_format = load_tasks()
    task_username = input("Enter the username to assign task to: ").strip()
    if task_username not in user_data:
        print("Username not found. Assign the task to a registered user.")
        return

    task_name = input("Enter title task: ").strip()
    task_description = input("Enter task description: ").strip()
    if not task_name or not task_description:
        print("Task title and description cannot be empty.")
        return

    while True:
        due_date = input("Enter Due Date (ex. December 12, 2026): ").strip()
        try:
            parse_date(due_date)
            break
        except ValueError:
            print("Invalid format. Please use 'Month Day, Year'.")

    tasks.append([
        task_username, task_name, task_description,
        datetime.now().strftime(DATE_FORMAT), due_date, "No",
    ])
    save_tasks(tasks, legacy_format)
    print("Task added successfully.")


def view_all():
    """Display every saved task with its details."""
    tasks, _ = load_tasks()
    if not tasks:
        print("No tasks found.")
        return

    for task in tasks:
        username, title, description, assigned, due, status = task
        print(f"""
------------------------------------
Task:           {title}
Assigned to:    {username}
Description:    {description}
Date Assigned:  {assigned}
Due Date:       {due}
Status:         {status}
------------------------------------
""")


def get_valid_task_number(max_range, prompt=None):
    """Read an in-range task number or -1 to cancel."""
    if prompt is None:
        prompt = "Enter task number to edit (-1 to exit): "
    while True:
        value = input(prompt).strip()
        if value == "-1":
            return -1
        try:
            selection = int(value)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        if 1 <= selection <= max_range:
            return selection
        print("Number out of range.")


def view_mine(curr_user):
    """Display and update tasks assigned to the logged-in user."""
    tasks, legacy_format = load_tasks()
    user_tasks = [
        (index, task) for index, task in enumerate(tasks)
        if task[0] == curr_user
    ]
    if not user_tasks:
        print("You have no tasks assigned.")
        return

    for number, (_, task) in enumerate(user_tasks, 1):
        print(f"{number}. Task: {task[1]} | Status: {task[5]}")

    selection = get_valid_task_number(len(user_tasks))
    if selection == -1:
        return
    index, original_task = user_tasks[selection - 1]
    task = original_task.copy()
    action = input(
        "Select: (c) Mark as Complete or (e) Edit due date/user: "
    ).strip().lower()

    if action == "c":
        task[5] = "Yes"
    elif action == "e":
        if task[5] == "Yes":
            print("Completed tasks cannot be edited.")
            return
        new_user = input("New username (leave blank to keep): ").strip()
        new_date = input("New due date (leave blank to keep): ").strip()
        if new_user and new_user not in user_data:
            print("Username not found. Task was not changed.")
            return
        if new_date:
            try:
                parse_date(new_date)
            except ValueError:
                print("Invalid due date. Task was not changed.")
                return
            task[4] = new_date
        if new_user:
            task[0] = new_user
    else:
        print("Invalid action. Task was not changed.")
        return

    tasks[index] = task
    save_tasks(tasks, legacy_format)
    print("Task updated successfully.")


def load_user_data():
    """Read local credentials, using the original fallback for a fresh run."""
    if not os.path.exists("user.txt"):
        print("user.txt not found. Using default admin login.")
        return {"admin": "password"}

    users = {}
    with open("user.txt", "r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, 1):
            if not line.strip():
                continue
            parts = line.strip().split(",")
            if len(parts) == 2:
                username, password = (part.strip() for part in parts)
                users[username] = password
            else:
                print(f"Warning: Skipping malformed line {line_number}.")
    return users


def view_completed():
    """Display tasks whose completion status is Yes."""
    tasks, _ = load_tasks()
    completed = [task for task in tasks if task[5] == "Yes"]
    if not completed:
        print("No completed tasks found.")
        return
    for task in completed:
        print(
            f"Task: {task[1]} | Assigned to: {task[0]} | Status: {task[5]}"
        )


def delete_task():
    """Delete one selected task, preserving every other complete record."""
    tasks, legacy_format = load_tasks()
    if not tasks:
        print("No tasks to delete.")
        return
    for number, task in enumerate(tasks, 1):
        print(f"{number}: {task[1]} | Assigned to: {task[0]}")

    selection = get_valid_task_number(
        len(tasks), "Enter the number of the task to delete (-1 to exit): "
    )
    if selection == -1:
        return
    deleted_task = tasks.pop(selection - 1)
    save_tasks(tasks, legacy_format)
    print(f"Deleted Task: {deleted_task[1]}")


def generate_reports(users=None):
    """Generate current task totals and per-user completion percentages."""
    if users is None:
        users = user_data
    tasks, _ = load_tasks()
    today = datetime.today().date()

    def is_overdue(task):
        return task[5] == "No" and parse_date(task[4]) < today

    total_tasks = len(tasks)
    completed_count = sum(task[5] == "Yes" for task in tasks)
    overdue_count = sum(is_overdue(task) for task in tasks)

    with open("task_overview.txt", "w", encoding="utf-8-sig") as file:
        file.write(f"Total Tasks: {total_tasks}\n")
        file.write(f"Completed: {completed_count}\n")
        file.write(f"Incomplete: {total_tasks - completed_count}\n")
        file.write(f"Overdue: {overdue_count}\n")

    with open("user_overview.txt", "w", encoding="utf-8-sig") as file:
        file.write(f"Total Users: {len(users)}\n")
        file.write(f"Total Tasks: {total_tasks}\n")
        file.write("-" * 30 + "\n")
        for username in users:
            assigned = [task for task in tasks if task[0] == username]
            user_total = len(assigned)
            user_completed = sum(task[5] == "Yes" for task in assigned)
            user_overdue = sum(is_overdue(task) for task in assigned)
            percent_assigned = (
                user_total / total_tasks * 100 if total_tasks else 0
            )
            percent_completed = (
                user_completed / user_total * 100 if user_total else 0
            )
            percent_incomplete = (
                (user_total - user_completed) / user_total * 100
                if user_total else 0
            )
            percent_overdue = (
                user_overdue / user_total * 100 if user_total else 0
            )
            file.write(f"User: {username}\n")
            file.write(f"  Task assigned: {user_total}\n")
            file.write(f"  % of Total Task: {percent_assigned:.2f}%\n")
            file.write(f"  % Completed: {percent_completed:.2f}%\n")
            file.write(f"  % Incomplete: {percent_incomplete:.2f}%\n")
            file.write(f"  % Overdue: {percent_overdue:.2f}%\n")
            file.write("-" * 20 + "\n")
    print("Reports generated successfully.")


def display_statistics(users):
    """Regenerate reports before displaying them so statistics stay current."""
    generate_reports(users)
    for filename in ("task_overview.txt", "user_overview.txt"):
        with open(filename, "r", encoding="utf-8-sig") as file:
            print(file.read())


def main():
    """Run login and the existing administrator/user task menus."""
    global user_data
    user_data = load_user_data()
    if not user_data:
        print("No valid accounts found. Check user.txt before logging in.")
        return

    while True:
        print("--- LOGIN ---")
        username = input("Username: ").strip()
        password = input("Password: ")
        if username in user_data and user_data[username] == password:
            print("Login successful!")
            curr_user = username
            break
        print("Invalid username or password. Please try again.")

    while True:
        if curr_user == "admin":
            menu = input('''Select one of the following options:
r - register user
a - add task
va - view all tasks
vm - view my tasks
vc - view completed tasks
ds - display statistics
del - delete tasks
e - exit
''').strip().lower()
        else:
            menu = input('''Select one of the following options:
r - register a user
a - add task
va - view all tasks
vm - view my tasks
e - exit
: ''').strip().lower()

        if menu == "e":
            print("Goodbye!!!")
            break
        if menu in {"r", "vc", "del", "ds"} and curr_user != "admin":
            print("Access denied. Only admin can use this option.")
            continue

        try:
            if menu == "r":
                reg_user(user_data)
            elif menu == "a":
                add_task()
            elif menu == "va":
                view_all()
            elif menu == "vm":
                view_mine(curr_user)
            elif menu == "vc":
                view_completed()
            elif menu == "del":
                delete_task()
            elif menu == "ds":
                display_statistics(user_data)
            else:
                print("You have entered an invalid input. Please try again.")
        except TaskDataError as error:
            print(f"Task data error: {error}")
        except OSError as error:
            print(f"File error: {error}")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!!!")
