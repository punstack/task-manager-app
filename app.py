# python -m venv .venv
# .venv/Scripts/activate
# https://getbootstrap.com/docs/4.3/getting-started/introduction/

from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_key_for_dev')
app.permanent_session_lifetime = timedelta(days=1)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' # "tasks" and "users" table
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Task(db.Model):
    __tablename__ = 'Task'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(200), default = None)
    checklist_item = db.Column(db.String(100), default = None)
    due_date = db.Column(db.Date, default = None)
    completed = db.Column(db.Boolean, default = False)
    user_lower = db.Column(db.String(20), nullable = False) # matches user_lower in "User" class

    def __init__(self, title, description, checklist_item, due_date, completed, user_lower):
        self.title = title  
        self.description = description
        self.checklist_item = checklist_item
        self.due_date = due_date
        self.completed = completed
        self.user_lower = user_lower

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(20), unique = True, nullable = False) # stores original case of username
    user_lower = db.Column(db.String(20), unique = True, nullable = False) # stores lower case version of username
    email = db.Column(db.String(100), unique = True, nullable = False)
    email_lower = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(50), nullable = False)

    def __init__(self, user, email, password):
        self.user = user
        self.user_lower = user.lower()
        self.email = email
        self.email_lower = email.lower()
        self.password = password

with app.app_context():
    #db.drop_all() # drop all tables // not necessary unless new columns are added to models
    db.create_all() # create tables based on models

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
        title = request.form["title"]
        description = request.form["description"] # else None
        checklist_item = request.form["checklist_item"] # else None
        due_date = request.form["due_date"] # else None # prints as YYYY-MM-DD
        try:
            if type(due_date) is str:
                due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except:
            due_date = None
        if "user" in session:
            user = session["user"]
        else:
            user = None
        new_task = Task(title = title, description = description, checklist_item = checklist_item, due_date = due_date, completed = False, user = user)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("user_page", user = session["user"]))
    else:
        return render_template('add_task.html')

@app.route("/login", methods = ["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("user_page", user = session["user"]))
    
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        stored_user = User.query.filter_by(user_lower = user.lower()).first() # this should be False if new user, True if existing user

        if stored_user and check_password_hash(stored_user.password, password):
            session.permanent = True
            session["user"] = stored_user.user # stores the orignal case in session
            return redirect(url_for("user_page", user = session["user"]))
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

@app.route("/<user>")
def user_page(user):    
    if "user" in session:
        logged_in_user = session["user"]
        if user.lower() != logged_in_user.lower():
            return render_template("user.html", user = user, tasks = Task.query.filter_by(user_lower=user.lower()).all())
        else:
            return render_template("user.html", user = logged_in_user, tasks = Task.query.filter_by(user_lower=logged_in_user.lower()).all())
    else:
        flash("To view profiles, you need to log in first.", "info")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        flash("You have been logged out.", "info")
        session.pop("user", None)   
    return redirect(url_for("login"))

#### FOR DEBUG USE

@app.route("/view")
def view():
    return render_template("view.html", values=Task.query.all())

@app.route("/view_users")
def view_users():
    return render_template("view_users.html", values=User.query.all())

@app.route("/settings")
def settings():
    if "user" in session:
        user = session["user"]
        stored_user = User.query.filter_by(user_lower = user.lower()).first()
    return render_template("settings.html", email = stored_user.email, user = user)
##################

if __name__ == '__main__':
    app.run(debug=True)

#TO-DO: should the web app have a social feature (friends/following/followers)?
#TO-DO: how would users see other peoples' tasks? HOW is there a social element in a task managing app?
#TO-DO: fix up home page to be pretty :)
#TO-DO: fix up my profile to be pretty
#TO-DO: add "completed" and "remove" buttons for all tasks
#TO-DO: add a session-user specific settings page that allows them to change email address, username, or password
#TO-DO: implement checking for used usernames
#TO-DO: implement password protection (eg. 8-24 characters, one number, one uppercase letter... doesn't have to be so specific)
#TO-DO: this is for later if this ever goes to prod, but add a "forgot password?" button linked to an email with a password reset OR a randomly generated password. not sure which is cooler
