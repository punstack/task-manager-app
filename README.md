# Task Manager Application
<p align="center">
  <img src="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDRzZW11c3B3ZjRqYnZwNnN3eXN6NmttZzcwdjA4NjBzbWRwMHR0NiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/AdBL4byLpKypsOLR9a/giphy.gif" />
</p>

Ever felt ovelwhelmed by your growing list of to-dos? Your friendly, neighborhood task manager has arrived! This project stores tasks and subtasks to a social network; tasks can be made private or public. Users can easily manage tasks, allowing them to maintain and easily visualize their list of to-dos.

This web application was built using the Flask framework with Python with HTML, CSS, and (very minimal) JavaScript for front-end design. The database is managed through SQLAlchemy.

## Run Locally
Clone the project:

```bash
  git clone https://github.com/punstack/task-manager-app.git
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

## Contents
- `app.py`: Contains and runs the web application.
- `functions.py`: Includes necessary functions to update user account.
- `models.py`: Defines the database tables (User, Task, Subtask) as Python classes.
- `view_task.py`: Establishes half of the routes in the web application related to tasks, including adding/updating/archiving a task and account settings.
- `view_user.py`: Establishes half of the routes in the web applicaiton related to the user, including the user profile, logging in, signing in, logging out, and the friends page.

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
This project was my first attempt at full-stack development. I originally had everything (database set-up, routes, and functions) in one file, `app.py`. It was incredibly difficult to debug, but it was very fulfilling to see the full web application! I don't intend to launch this on a website or anything, but it was a very fun project to share locally.

If you're interested, check out my previous commits to see how the `app.py` file has changed over time!

## Feedback

If you have any feedback, please message me on GitHub! I'd love to hear what others think about this project, as I haven't done much front-end design aside from dashboards in PowerBI or graphs purely using Python.
