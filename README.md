# Task Manager Application

Ever felt overwhelmed by your growing list of to-dos? Your friendly, neighborhood task manager has arrived! This project stores tasks and subtasks to a social network; tasks can be made private or public. Users can easily manage tasks, allowing them to maintain and easily visualize their list of to-dos.

This web application was built using the Flask framework with Python with HTML, CSS, and (very minimal) JavaScript for front-end design. The database is managed through SQLAlchemy.

## Run Locally

Clone the project:

```bash
  git clone https://github.com/punstack/task-manager-app
```

Go to the project directory:

```bash
  cd task-manager-app
```

Set up a virtual environment:

```bash
  python -m venv .venv
```

Activate the virtual environment:

```bash
  .venv/Scripts/activate
```
Install dependencies:

```bash
  pip install -r requirements.txt
```

Start the application:

```bash
  python app.py
```

## Features

- User authentication:
    - Unique usernames
    - Hashed passwords
- User interactions:
    - Search for friends
    - Send, accept, or deny friend requests
    - Remove friends
- Task and subtask creation:
    - Add, update, archive, and delete tasks
    - Public or private tasks
    - Database supports many tasks per user
## Lessons Learned

This project was my first attempt at full-stack development. I originally had everything (database set-up, routes, and functions) in one file, `app.py`. It was incredibly difficult to debug, but it was very fulfilling to see the full web application! I don't intend to launch this publically, but it was a very fun project to share with my friends nearby.

If you're interested, check out my previous commits to see how the `app.py` file has changed over time!
## Feedback

If you have any feedback, please message me on GitHub! I'd love to hear what others think about this project, as I haven't done much front-end design aside from dashboards in PowerBI or graphs purely using Python.
