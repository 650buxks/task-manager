import os
from datetime import datetime


# Register new Users
def reg_user(user_data):
    """
    Handles the registration of new users. Checks if a username already exists
    in the current data to prevent duplicates and ensures the password matches
    a confirmation entry before appending the new credentials to user.txt.
    """
    username = input("Enter new Username: ")
    if username in user_data:
        print("Username already used.")
        return

    password = input("Enter new Password: ")
    confirmed_password = input("Retype same password: ")

    if password == confirmed_password:
        with open("user.txt", "a", encoding="utf-8-sig") as file:
            file.write(f"{username}, {password}\n")
        user_data[username] = password
        print("User registered successfully.")
    else:
        print("Invalid password. Please match the password.")


# Add tasks
def add_task():
    """
    Allows a user to create new task. It captures assigned username,
    title, and description, automatically generates today's date,
    and uses a while loop with strptime to force the user to enter
    a valid due date format before saving it to tasks.txt.
    """
    task_username = input("Enter the username to assign task to: ")
    task_name = input("Enter title task: ")
    task_description = input("Enter task description: ")

    today_date = datetime.now().strftime("%B %d, %Y")

    while True:
        due_date = input("Enter Due Date (ex. December 12, 2022): ")
        try:
            datetime.strptime(due_date, "%B %d, %Y")
            break
        except ValueError:
            print(
                "Invalid format, Please use format 'Month Day, Year'"
                )

    task_completion = "No"

    with open("tasks.txt", "a", encoding="utf-8-sig") as file:
        file.write(
            f"{task_username}, {task_name}, {task_description}, "
            f"{today_date}, {due_date}, {task_completion}\n"
            )
        print("Task added successfully.")


# Views all tasks assigned to users
def view_all():
    """
    Reads tasks.txt and prints every task stored in the file to the console.
    It includes a debug feature to verify the data structure and uses a
    visually separated block of text to make tasks easy for users to read.
    """
    with open("tasks.txt", "r", encoding="utf-8-sig") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            parts = line.split(",")
            print(f"DEBUG: I found {len(parts)} parts in this line: {line}")
            if len(parts) == 6:
                (task_username, task_name, task_description,
                 today_date, due_date, task_completion) = parts
                print(f"""
------------------------------------
Task:           {task_name}
Assigned to:    {task_username}
Description:    {task_description}
Date Assigned:  {today_date}
Due Date:       {due_date}
Status:         {task_completion}
------------------------------------
""")
            else:
                print(f"skipping corrupt task data: {line}")


def get_valid_task_number(max_range):
    """
    A helper function that ensures user input for selecting a task
    is valid integer within the allowed range. It uses recursion to
    keep asking the user for a number until they provide a valid one
    or choose to exit.
    """
    user_input = input("Enter task number to edit (-1 to exit): ")

    if user_input == "-1":
        return -1

    try:
        selection = int(user_input)
        if 1 <= selection <= max_range:
            return selection
        else:
            print("Number out of range")
            return get_valid_task_number(max_range)
    except ValueError:
        print("Invalid input. Please enter a number.")
        return get_valid_task_number(max_range)


# Views the current user's tasks
def view_mine(curr_user):
    """
    Filters the master task list to show only tasks assigned to
    the current logged-in user. It also provides an interactive
    menu allowing users to mark a specific task as complete or
    edit the task's details (username/due date).
    """
    with open("tasks.txt", "r", encoding="utf-8-sig") as file:
        task_list = file.readlines()

    user_tasks = []
    for i, line in enumerate(task_list):
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) == 6 and parts[0].strip() == curr_user:
            user_tasks.append((i, parts))

    if not user_tasks:
        print(" You have no tasks assigned.")
        return

    for idx, (original_index, task) in enumerate(user_tasks, 1):
        print(f"{idx}. Task: {task[1]} | Status: {task[5]}")

    try:
        selection = get_valid_task_number(len(user_tasks))
        if selection == -1:
            return

        if 1 <= selection <= len(user_tasks):
            original_idx, task_data = user_tasks[selection - 1]

            action = input(
                "Select: (c) Mark as Complete or (e) Edit due date/user: "
                ).lower()

            if action == 'c':
                task_data[5] = "Yes"
            elif action == 'e' and task_data[5].strip().lower() == "no":
                new_user = input("New username (leave blank to keep): ")
                new_date = input("New due date (leave blank to keep): ")
                if new_user:
                    task_data[0] = new_user
                if new_date:
                    task_data[4] = new_date

            task_list[original_idx] = ", ".join(task_data) + "\n"

            with open("tasks.txt", "w", encoding="utf-8-sig") as file:
                file.writelines(task_list)
            print("Task updated successfully.")
    except ValueError:
        print("Invalid input")


# Loads data from user.txt file
def load_user_data():
    """
    The "gatekeeper" function that runs at startup. It reads user.txt,
    parses the usernames and passwords into a dictionary, and provides
    a default admin account if the file is missing so the program can
    still start.
    """
    if not os.path.exists("user.txt"):
        print("Error: user.txt file not found. Using default admin login")
        return {"admin": "password"}

    data = {}
    with open("user.txt", "r", encoding="utf-8-sig") as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            if not line:
                continue

            if "," in line:
                parts = line.split(",")
                if len(parts) == 2:
                    u = parts[0].strip()
                    p = parts[1].strip()
                    data[u] = p
            else:
                print(
                    f"Warning: Skipping malformed line {line_num} in user.txt"
                    )
    return data


# Views completed tasks
def view_completed():
    """
    Scans tasks.txt and displays only the tasks where the completion status
    is set to 'Yes'. It's an administrative tool to quickly see finished work.
    """
    if not os.path.exists("tasks.txt"):
        print("No tasks found.")
        return

    with open("tasks.txt", "r", encoding="utf-8-sig") as file:
        found_any = False
        for line in file:
            line = line.strip()
            if not line:
                continue

            parts = line.split(",")
            if len(parts) == 6 and parts[5].strip().lower() == "yes":
                print(
                    f"Task: {parts[1]} | Assigned to: {parts[0]} | "
                    f"Status: {parts[5]}"
                    )
                found_any = True

        if not found_any:
            print("No completed tasks found.")


# Picks tasks to delete from task.txt file
def delete_task():
    """
    Allows the admin to remove a task entirely from the records. Displays
    a numbered list of all tasks, takes a user selection, pops that line
    from the list, and overwrites tasks.txt with the remaining data
    """
    if not os.path.exists("tasks.txt"):
        print("No tasks to delete.")
        return

    with open("tasks.txt", "r", encoding="utf-8-sig") as file:
        lines = file.readlines()

    if not lines:
        print("Task list is empty.")
        return

    for i, line in enumerate(lines, 1):
        print(f"{i}: {line.strip()}")

    try:
        choice = int(input(
            "Enter the number of the task to delete (-1 to exit): "
            ))
        if choice == -1:
            return

        if 1 <= choice <= len(lines):
            deleted_task = lines.pop(choice - 1)
            with open("tasks.txt", "w", encoding="utf-8-sig") as file:
                file.writelines(lines)

            task_name = deleted_task.split(',')[1]
            print(f"Deleted Task: {task_name}")
        else:
            print("Invalid Number. Please choose number from list.")
    except ValueError:
        print("Invalid input. Please enter a number.")


# Creates a report titled user_overview.txt and task_overview.txt
# Shows the total task, complete/incomplete tasks, overdue task,
# and shows the percentages of complete/incomplete tasks
def generate_reports():
    """
    Performs the heavy lifting for data analysis. Calculates totals
    for tasks, users, completion percentages, and overdue status,
    then writes these summaries into two text files: task_overview.txt
    and user_overview.txt
    """
    if not os.path.exists("tasks.txt"):
        return

    with open("tasks.txt", "r", encoding="utf-8-sig") as file:
        task_data = file.readlines()

    total_tasks = len(task_data)
    total_users = len(user_data)
    today = datetime.today()

    completed_count = 0
    overdue_count = 0

    for line in task_data:
        parts = line.strip().split(",")
        if len(parts) == 6:
            if parts[5].strip().lower() == "yes":
                completed_count += 1
            due_date = datetime.strptime(parts[4].strip(), "%B %d, %Y")
            if parts[5].strip().lower() == "no" and due_date < today:
                overdue_count += 1

    with open("task_overview.txt", "w", encoding="utf-8-sig") as f:
        f.write(f"Total Tasks: {total_tasks}\n")
        f.write(f"Completed: {completed_count}\n")
        f.write(f"Incomplete: {total_tasks - completed_count}\n")
        f.write(f"Overdue: {overdue_count}\n")

    with open("user_overview.txt", "w", encoding="utf-8-sig") as f:
        f.write(f"Total Users: {total_users}\n")
        f.write(f"Total Tasks: {total_tasks}\n")
        f.write("-" * 30 + "\n")

        for user in user_data:
            user_total = 0
            user_completed = 0
            user_overdue = 0

            for line in task_data:
                parts = line.strip().split(",")
                if len(parts) == 6 and parts[0] == user:
                    user_total += 1
                    if parts[5].lower() == "yes":
                        user_completed += 1
                    try:
                        due_str = parts[4].strip()
                        due_date = datetime.strptime(due_str, "%B %d, %Y")
                        if parts[5].lower() == "no" and due_date < today:
                            user_overdue += 1
                    except ValueError:
                        pass

            if user_total > 0:
                perc_assigned = (
                    (user_total / total_tasks) * 100
                )
                perc_completed = (
                    (user_completed / user_total) * 100
                )
                perc_incomplete = (
                    ((user_total - user_completed) / user_total) * 100
                )
                perc_overdue = (
                    (user_overdue / user_total) * 100
                )
            else:
                perc_assigned = perc_completed = perc_incomplete = 0
                perc_overdue = 0

            f.write(f"User: {user}\n")
            f.write(f"  Task assigned: {user_total}\n")
            f.write(f"  % of Total Task: {perc_assigned:.2f}%\n")
            f.write(f"  % Completed: {perc_completed:.2f}%\n")
            f.write(f"  % Incomplete: {perc_incomplete:.2f}%\n")
            f.write(f"  % Overdue: {perc_overdue:.2f}%\n")
            f.write("-" * 20 + "\n")

    print("Reports generated successfully.")


# Shows number of users and tasks
def display_statistics(user_data):
    """
    A simple display tool that reads the generated report files
    (task_overview.txt and user_overview.txt) and prints their contents
    to the screen for the admin to view within the app.
    """
    if (not os.path.exists("task_overview.txt") or
            not os.path.exists("user_overview.txt")):
        generate_reports()

    with open("task_overview.txt", "r") as f:
        print(f.read())

    with open("user_overview.txt", "r", encoding="utf-8-sig") as f:
        print(f.read())


logged_in = False
curr_user = ""
user_data = load_user_data()


# Login page
while not logged_in:
    print("--- LOGIN ---")
    username_input = input("Username: ")
    password_input = input("Password: ")

    if (username_input in user_data and
            user_data[username_input] == password_input):
        print("Login successful!")
        curr_user = username_input
        logged_in = True
    else:
        print("Invalid username or password. Please try again.")


# Admin's menu
while True:
    if curr_user == "admin":
        menu = input('''Select of the following options:
r - register user
a - add task
va - view all tasks
vm - view my tasks
vc - view completed tasks
ds - display statistics
del - delete tasks
e - exit
''').lower()

# Regular user's menu
    else:
        menu = input('''Select one of the following options:
r - register a user
a - add task
va - view all tasks
vm - view my tasks
e - exit
: ''').lower()

    if menu == 'r' and curr_user == "admin":
        reg_user(user_data)
    elif menu == 'r' and curr_user != "admin":
        print("Access denied. Only admin can register users.")
    elif menu == 'a':
        add_task()
    elif menu == 'va':
        view_all()
    elif menu == 'vm':
        view_mine(curr_user)
    elif menu == 'vc' and curr_user == "admin":
        view_completed()
    elif menu == 'vc' and curr_user != "admin":
        print("Access Denied. Only admin can view all tasks.")
    elif menu == 'del' and curr_user == "admin":
        delete_task()
    elif menu == 'ds' and curr_user == "admin":
        display_statistics(user_data)
    elif menu == 'del' and curr_user != "admin":
        print("Access Denied. Only admin can delete tasks.")
    elif menu == 'e':
        print('Goodbye!!!')
        break
    else:
        print("You have entered an invalid input. Please try again")
