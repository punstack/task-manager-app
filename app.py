# python -m venv .venv
# .venv/Scripts/activate
# https://getbootstrap.com/docs/4.3/getting-started/introduction/

from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import uuid
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_key_for_dev')
app.permanent_session_lifetime = timedelta(days=1)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' # "tasks" and "users" table
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

friends = db.Table('friends',
    db.Column('user_id', db.String(36), db.ForeignKey('User.id'), primary_key = True),
    db.Column('friend_id', db.String(36), db.ForeignKey('User.id'), primary_key = True),
    db.Column('is_accepted', db.Boolean, default = False) # need to check if this is still usable??
)

class Subtask(db.Model):
    __tablename__ = 'Subtask'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), default = None)
    completed = db.Column(db.Boolean, default = False)
    task_id = db.Column(db.Integer, db.ForeignKey('Task.id', ondelete='CASCADE'), nullable = False)

    def __init__(self, title, completed, task_id):
        self.title = title
        self.completed = completed
        self.task_id = task_id

class Task(db.Model):
    __tablename__ = 'Task'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(200), default = None)
    due_date = db.Column(db.Date, default = None)
    completed = db.Column(db.Boolean, default = False)
    task_status = db.Column(db.Boolean, default = False, nullable = False) # False = private, True = public
    archive_status = db.Column(db.Boolean, default = False, nullable = False) # False = not archived, True = archived
    user_id = db.Column(db.String(36), db.ForeignKey('User.id', ondelete='CASCADE'), nullable = False) # matches id in "User" class
    
    subtasks = db.relationship('Subtask', backref='task', lazy = True, cascade = 'all, delete-orphan')

    def __init__(self, title, description, due_date, completed, task_status, archive_status, user_id):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.completed = completed
        self.task_status = task_status
        self.archive_status = archive_status
        self.user_id = user_id

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.String(36), primary_key = True, default=lambda: str(uuid.uuid4()))
    user = db.Column(db.String(20), unique = True, nullable = False) # stores original case of username
    user_lower = db.Column(db.String(20), unique = True, nullable = False) # stores lower case version of username
    email = db.Column(db.String(100), unique = True, nullable = False)
    email_lower = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(50), nullable = False)
    tasks = db.relationship('Task', backref='user', lazy = True, cascade = 'all, delete-orphan')
    friends = db.relationship('User',
                              secondary = friends,
                              primaryjoin = (friends.c.user_id == id),
                              secondaryjoin = (friends.c.friend_id == id),
                              backref = db.backref('friended_by', lazy = 'dynamic'), # for loading 'friended_by'
                              lazy = 'dynamic') # for loading 'friends'

    def __init__(self, user, email, password):
        self.user = user
        self.user_lower = user.lower()
        self.email = email
        self.email_lower = email.lower()
        self.password = password

    ### OPERATIONS FOR INTERACTING WITH OTHER USERS

    def send_friend_request(self, user):
        if not self.has_pending_request(user) and not self.is_friend_with(user):
            new_request = FriendRequest(sender_id=self.id, receiver_id=user.id)
            db.session.add(new_request)
            db.session.commit()

    def is_friend_with(self, user):
        return self.friends.filter(friends.c.friend_id == user.id).count() > 0

    def accept_friend_request(self, user):
        friend_request = FriendRequest.query.filter_by(sender_id=user.id, receiver_id=self.id).first()
        if friend_request:
            self.friends.append(user)
            user.friends.append(self)
            db.session.delete(friend_request)
            db.session.commit()

    def decline_friend_request(self, user): # make sure this works
        friend_request = FriendRequest.query.filter_by(sender_id=user.id, receiver_id=self.id).first()
        if friend_request:
            db.session.delete(friend_request)
            db.session.commit()

    def remove_friend(self, user):
        if self.is_friend_with(user):
            self.friends.remove(user)
            user.friends.remove(self)
            db.session.commit()

    def has_pending_request(self, user): # OUTGOING friend requests
        return FriendRequest.query.filter_by(sender_id=self.id, receiver_id=user.id).count() > 0
    ###

class FriendRequest(db.Model):
    __tablename__ = 'FriendRequest'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    sender_id = db.Column(db.String(36), db.ForeignKey('User.id'), nullable=False)
    receiver_id = db.Column(db.String(36), db.ForeignKey('User.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now())

    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_requests', lazy='dynamic', cascade='all, delete-orphan'))
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref=db.backref('received_requests', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<FriendRequest from {self.sender.username} to {self.receiver.username}>'

with app.app_context():
    #db.drop_all() # drop all tables // not necessary unless new columns are added to models
    db.create_all() # create tables based on models

@app.before_request
def check_user_existence():
    if "user" in session:
        user_lower = session["user"].lower()
        if not User.query.filter_by(user_lower=user_lower).first():
            session.pop("user", None)
            return redirect(url_for("login"))

@app.route('/')
def index():
    # remove all entries in the database
    '''
    for task in Task.query.all():
        Task.query.delete()
    db.session.commit()

    for user in User.query.all():
        User.query.delete()
    db.session.commit()
    '''
    return render_template('index.html')

@app.route('/add-task', methods = ["GET", "POST"])
def add_task():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description", "")  # Default to empty string if None
        subtasks = request.form.getlist("subtask[]")
        due_date = request.form.get("due_date")
        task_status = request.form.get("task_status") # False = private, True = public
        task_id = request.form.get("task_id")

        try:
            if isinstance(due_date, str) and due_date:
                due_date = datetime.strptime(due_date, '%Y-%m-%d')
            else:
                due_date = None
        except Exception as e:
            flash(f"An error occurred while processing the due date: {str(e)}", "error")
            due_date = None

        if task_status == "true":
            task_status = True
        elif task_status == "false":
            task_status = False
        else:
            flash("Invalid task status", "error")
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

        return redirect(url_for("user_page", user=session["user"]))
    
    task_id = request.args.get('task_id')
    if task_id:
        task = Task.query.get_or_404(task_id)
        subtasks = [subtask.title for subtask in task.subtasks]
        return render_template('add_task.html', task=task, subtasks=subtasks)
    
    return render_template('add_task.html')

@app.route('/update-task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = not task.completed  # toggle the status
        db.session.commit()
        return {"success": True, "completed": task.completed}
    return {"success": False}, 404

@app.route('/update-subtask/<int:subtask_id>', methods=['POST'])
def update_subtask(subtask_id):
    subtask = Subtask.query.get_or_404(subtask_id)
    if subtask:
        subtask.completed = not subtask.completed
        db.session.commit()
        return {"success": True, "completed": subtask.completed}
    return {"success": False}, 404

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("user_page", user=session["user"]))

    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        # query using lower-case username
        stored_user = User.query.filter_by(user_lower=user.lower()).first()

        if stored_user and check_password_hash(stored_user.password, password):
            session.permanent = True
            session["user"] = stored_user.user  # store the original case in session
            return redirect(url_for("user_page", user=stored_user.user))
        else:
            flash("The credentials you have entered do not match our system.", "error")
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route("/sign-up", methods = ["GET", "POST"])
def signup():
    if "user" in session:
        return redirect(url_for("user_page", user = session["user"]))

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
            return redirect(url_for("user_page", user = session["user"]))
    else:
        return render_template("signup.html")

def friend_request_status(user, other):
    if request.method == "POST":
        friend_request_status = request.form["request"]

        if friend_request_status == "-1": # already friends, remove friend
            user.remove_friend(other)
        elif friend_request_status == "0": # friend request denied
            user.decline_friend_request(other)
        elif friend_request_status == "1": # friend request accepted
            user.accept_friend_request(other)
        elif friend_request_status == "2": # send friend request
            user.send_friend_request(other)

@app.route("/<user>", methods = ["GET", "POST"])
def user_page(user):
    if "user" in session:
        # information for passed dictionary
        info = {
            'stored_user': User.query.filter_by(user_lower=session["user"].lower()).first(),
            'viewed_user': None,
            'tasks': None,
        }

        if not info["stored_user"]:
            flash("Your account has been deleted. Please log in again.", "error")
            session.pop("user", None)
            return redirect(url_for("login"))

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
                elif dropdown_request == "1": # task to be appended
                    return redirect(url_for('add_task', task_id = task.id))
                
            return render_template("user.html", user = info["stored_user"].user, info = info)
        else:
            # if the logged-in user is viewing an existing profile
            info["viewed_user"] = User.query.filter_by(user_lower=user.lower()).first()
            if info["viewed_user"]:
                info["tasks"] = info["viewed_user"].tasks
                friend_request_status(info["stored_user"], info["viewed_user"])
                return render_template("user.html", user = info["viewed_user"].user, info = info)
            # if the logged-in user is viewing a non-existent profile
            else:
                flash("User not found.", "error")
                info["tasks"] = info["stored_user"].tasks
                return redirect(url_for("user_page", user = session["user"]))

    flash("To view profiles, you need to log in first.", "info")
    return redirect(url_for("login"))

@app.route("/archive", methods = ["GET", "POST"])
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
        elif dropdown_request == "0": # task to be achived
            task.archive_status = False
            db.session.commit()
            flash("Task unarchived.", "success")
            info["tasks"] = info["stored_user"].tasks
    
    return render_template("archive.html", info = info)

def delete_status(user):
    try:
        delete_status = request.form["delete_status"]

        if delete_status == "-1": # delete account
            try:
                db.session.delete(user)
                db.session.commit()
                session.pop("user", None)
                flash("Your account has been deleted. Please log in again.", "error")
                return redirect(url_for("login"))
            except Exception as e:
                db.session.rollback()  
                flash(f"An error occured while trying to delete the account: {str(e)}", "error")
                return redirect(url_for("settings"))
    except:
        return render_template("settings.html", email=user.email, user=session["user"])
     
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user" in session:
        # fetch user using the session username
        stored_user = User.query.filter_by(user_lower=session["user"].lower()).first()

        if request.method == "POST":
            # check if user is deleting account
            delete_status(stored_user)
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
                return redirect(url_for("user_page", user=new_username))

            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}", "error")
                return render_template("settings.html", email=stored_user.email, user=session["user"])

        return render_template("settings.html", email=stored_user.email, user=session["user"])

    flash("You need to log in first.", "error")
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        flash("You have been logged out.", "info")
        session.pop("user", None)
    return redirect(url_for("login"))

#### FOR DEBUG USE

@app.route("/view_users")
def view_users():
    return render_template("view_users.html", values=User.query.all())

if __name__ == '__main__':
    app.run(debug=True)