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
    user = db.Column(db.String(20), nullable = False) # matches user in "User" class

    def __init__(self, title, description, checklist_item, due_date, completed, user):
        self.title = title
        self.description = description
        self.checklist_item = checklist_item
        self.due_date = due_date
        self.completed = completed
        self.user = user

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(20), nullable = False) # matches user in "Task" class
    email = db.Column(db.String(100), nullable = False)
    password = db.Column(db.String(50), nullable = False)

    def __init__(self, user, email, password):
        self.user = user
        self.email = email
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
        user = request.form["username"].lower()
        password = request.form["password"]

        stored_user = User.query.filter_by(user = user.lower()).first() # this should be False if new user, True if existing user

        if stored_user and check_password_hash(stored_user.password, password):
            print("the if statement won")
            session.permanent = True
            session["user"] = user
            return redirect(url_for("user_page", user = session["user"]))
        else:
            print("the else statement won")
            # TODO: fix flash statements
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

        stored_user = User.query.filter_by(user = user).first() # this should be False if new user, True if existing user

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
        print("Made it in session!")
        logged_in_user = session["user"]

        if user != logged_in_user:
            print("Am not logged in user!")
            return render_template("user.html", user = user, tasks = Task.query.filter_by(user=user).all())
        else:
            print("Logged in user!")
            return render_template("user.html", user = logged_in_user, tasks = Task.query.filter_by(user=logged_in_user).all())
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
##################

if __name__ == '__main__':
    app.run(debug=True)