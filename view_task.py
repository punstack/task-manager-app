from flask import Blueprint, render_template, redirect, request, url_for, session, flash
from werkzeug.security import generate_password_hash
from models import User, Task, Subtask, db
from datetime import datetime
import functions

view_task = Blueprint("view_task", __name__, static_folder = 'static', template_folder = 'templates')

@view_task.before_request
def check_user_existence():
    if "user" in session:
        user_lower = session["user"].lower()
        if not User.query.filter_by(user_lower=user_lower).first():
            session.pop("user", None)
            return redirect(url_for("view_user.login"))

@view_task.route('/add-task', methods = ["GET", "POST"])
def add_task():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description", "")
        subtasks = request.form.getlist("subtask[]")
        due_date = request.form.get("due_date")
        task_status = request.form.get("task_status") # False = private, True = public
        task_id = request.form.get("task_id")

        if isinstance(due_date, str) and due_date:
            due_date = datetime.strptime(due_date, '%Y-%m-%d')
        else:
            due_date = None

        if task_status == "true":
            task_status = True
        else:
            task_status = False

        if "user" in session:
            user = session["user"].lower()
            stored_user = User.query.filter_by(user_lower=user).first()
        
        if task_id: # updates existing task
            task = Task.query.get_or_404(task_id)
            task.title = title
            task.description = description
            task.due_date = due_date
            task.task_status = task_status
        else:
            task = Task(title = title, description = description, due_date = due_date, completed = False, task_status = task_status, archive_status = False, user_id = stored_user.id)
            db.session.add(task)
        
        db.session.flush()

        Subtask.query.filter_by(task_id=task.id).delete()  # remove existing subtasks associated with original task
        for subtask in subtasks:
            if subtask.strip():
                new_subtask = Subtask(title=subtask, completed=False, task_id=task.id)
                db.session.add(new_subtask)
        db.session.commit()

        return redirect(url_for("view_user.user_page", user=session["user"]))
    
    task_id = request.args.get('task_id')
    if task_id:
        task = Task.query.get_or_404(task_id)
        subtasks = [subtask.title for subtask in task.subtasks]
        return render_template('add_task.html', task=task, subtasks=subtasks)
    
    return render_template('add_task.html')

@view_task.route('/update-task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = not task.completed  # toggle the status
        db.session.commit()
        return {"success": True, "completed": task.completed}
    return {"success": False}, 404

@view_task.route('/update-subtask/<int:subtask_id>', methods=['POST'])
def update_subtask(subtask_id):
    subtask = Subtask.query.get_or_404(subtask_id)
    if subtask:
        subtask.completed = not subtask.completed
        db.session.commit()
        return {"success": True, "completed": subtask.completed}
    return {"success": False}, 404

@view_task.route("/archive", methods = ["GET", "POST"])
def archive():
    stored_user = User.query.filter_by(user_lower=session["user"].lower()).first()
    info = {
        'stored_user': stored_user,
        'tasks': stored_user.tasks
    }

    if request.method == "POST": # logged-in user does a request on current task
        dropdown_request = request.form["dropdown"]
        task_id = int(request.form.get("task_id"))
        task = Task.query.get(task_id)

        if dropdown_request == "-1": # task to be deleted
            db.session.delete(task)
            db.session.commit()
            flash("Task deleted.", "success")
            info["tasks"] = info["stored_user"].tasks
        elif dropdown_request == "0": # task to be unachived
            task.archive_status = False
            db.session.commit()
            flash("Task unarchived.", "success")
            info["tasks"] = info["stored_user"].tasks
    
    return render_template("archive.html", info = info)

@view_task.route("/settings", methods=["GET", "POST"])
def settings():
    if "user" in session:
        # fetch user using the session username
        stored_user = User.query.filter_by(user_lower=session["user"].lower()).first()

        if request.method == "POST":
            # check if user is deleting account
            functions.delete_status(stored_user)
            # if user not deleting account, then user is probably updating something
            new_email = request.form["email"]
            new_username = request.form["username"]
            new_password = request.form["password"]

            # check if the new username is already taken
            existing_user = User.query.filter_by(user_lower=new_username.lower()).first()
            if existing_user and existing_user.user_lower != stored_user.user_lower:
                flash("Username already taken. Please choose a different username.", "error")
                return render_template("settings.html", email=stored_user.email, user=session["user"])

            # update user details
            stored_user.user = new_username
            stored_user.email = new_email
            stored_user.user_lower = new_username.lower() # ensure the lower case version is updated

            if len(new_password) > 0:
                new_hashed_password = generate_password_hash(new_password, method="pbkdf2:sha256")
                stored_user.password = new_hashed_password

            try:
                db.session.commit()

                # update session with new username
                session["user"] = new_username

                flash("Your credentials have been updated.", "info")
                return redirect(url_for("view_user.user_page", user=new_username))

            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}", "error")
                return render_template("settings.html", email=stored_user.email, user=session["user"])

        return render_template("settings.html", email=stored_user.email, user=session["user"])

    flash("You need to log in first.", "error")
    return redirect(url_for("view_user.login"))

@view_task.route("/search", methods = ["GET"])
def search():
    query = request.args.get('query', '') # from front-end; defaults to empty string if no query is provided
    results = functions.search_tasks(query)
    return render_template("search.html", results = results)