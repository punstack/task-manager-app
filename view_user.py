from flask import Blueprint, render_template, redirect, request, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Task, FriendRequest, db
import functions

view_user = Blueprint("view_user", __name__, static_folder = 'static', template_folder = 'templates')

@view_user.before_request
def check_user_existence():
    if "user" in session:
        user_lower = session["user"].lower()
        if not User.query.filter_by(user_lower=user_lower).first():
            session.pop("user", None)
            return redirect(url_for("view_user.login"))

@view_user.route('/')
def index():
    return render_template('index.html')

@view_user.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("view_user.user_page", user=session["user"]))

    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        # query using lower-case username
        stored_user = User.query.filter_by(user_lower=user.lower()).first()

        if stored_user and check_password_hash(stored_user.password, password):
            session.permanent = True
            session["user"] = stored_user.user  # store the original case in session
            return redirect(url_for("view_user.user_page", user=stored_user.user))
        else:
            flash("The credentials you have entered do not match our system.", "error")
            return render_template("login.html")
    else:
        return render_template("login.html")

@view_user.route("/sign-up", methods = ["GET", "POST"])
def signup():
    if "user" in session:
        return redirect(url_for("view_user.user_page", user = session["user"]))

    if request.method == "POST":
        email = request.form["email"]
        user = request.form["username"]
        password = request.form["password"]

        stored_user = User.query.filter_by(user_lower = user.lower()).first() # this should be False if new user, True if existing user
        stored_email = User.query.filter_by(email_lower = email.lower()).first()

        if stored_email:
            flash("An account with this email already exists. Please log in.", "info")
            return render_template("signup.html")
        if stored_user:
            flash("An account with this username already exists. Please log in.", "info")
            return render_template("signup.html")
        else:
            session['user'] = user
            hashed_password = generate_password_hash(password, method = "pbkdf2:sha256")
            new_user = User(user = user, email = email, password = hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("view_user.user_page", user = session["user"]))
    else:
        return render_template("signup.html")

@view_user.route("/<user>", methods = ["GET", "POST"])
def user_page(user):
    if "user" in session:
        info = {
            'stored_user': User.query.filter_by(user_lower=session["user"].lower()).first(),
            'viewed_user': None,
            'tasks': None,
        }

        if not info["stored_user"]:
            flash("Your account has been deleted. Please log in again.", "error")
            session.pop("user", None)
            return redirect(url_for("view_user.login"))

        # if the logged-in user is viewing their own profile, use re-queried user data
        if user.lower() == info["stored_user"].user_lower:
            info["tasks"] = info["stored_user"].tasks

            if request.method == "POST": # logged-in user does a request on current task
                dropdown_request = request.form["dropdown"]
                task_id = int(request.form.get("task_id"))
                task = Task.query.get(task_id)

                if dropdown_request == "-1": # task to be deleted
                    db.session.delete(task)
                    db.session.commit()
                    flash("Task deleted.", "success")
                    info["tasks"] = info["stored_user"].tasks
                elif dropdown_request == "0": # task to be achived
                    task.archive_status = True
                    db.session.commit()
                    flash("Task archived.", "success")
                    info["tasks"] = info["stored_user"].tasks
                elif dropdown_request == "1": # task to be viewended
                    return redirect(url_for('view_task.add_task', task_id = task.id))
                
            return render_template("user.html", user = info["stored_user"].user, info = info)
        else:
            # if the logged-in user is viewing an existing profile
            info["viewed_user"] = User.query.filter_by(user_lower=user.lower()).first()
            if info["viewed_user"]:
                info["tasks"] = info["viewed_user"].tasks
                functions.friend_request_status(info["stored_user"], info["viewed_user"])
                return render_template("user.html", user = info["viewed_user"].user, info = info)
            # if the logged-in user is viewing a non-existent profile
            else:
                flash("User not found.", "error")
                info["tasks"] = info["stored_user"].tasks
                return redirect(url_for("view_user.user_page", user = session.get("user", "")))#session["user"]))

    flash("To view profiles, you need to log in first.", "info")
    return redirect(url_for("view_user.login"))

@view_user.route("/friends")
def friends_page():
    stored_user = User.query.filter_by(user_lower=session["user"].lower()).first()
    # outgoing friend requests
    outgoing_requests = FriendRequest.query.filter_by(sender_id = stored_user.id)
    outgoing_user = [User.query.get(request.receiver_id) for request in outgoing_requests]
    outgoing_users = [out.user for out in outgoing_user]
    # incoming friend requests
    incoming_requests = FriendRequest.query.filter_by(receiver_id = stored_user.id)
    incoming_user = [User.query.get(request.sender_id) for request in incoming_requests]
    incoming_users = [inc.user for inc in incoming_user]

    friends_list = stored_user.friends.all()
    friends_users = [friend.user for friend in friends_list]
    
    info =  {
        'stored_user': stored_user,
        'outgoing': outgoing_users,
        'incoming': incoming_users,
        'friends': friends_users
    }
    return render_template("friends.html", info = info)

@view_user.route("/logout")
def logout():
    if "user" in session:
        flash("You have been logged out.", "info")
        session.pop("user", None)
    return redirect(url_for("view_user.login"))