# python -m venv .venv
# source  .venv/Scripts/activate

from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "rehash-necessary"
app.permanent_session_lifetime = timedelta(days=1)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' # "tasks" and "users" table
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(200), default = None)
    checklist_item = db.Column(db.String(100), default = None)
    due_date = db.Column(db.DateTime, default = None)
    completed = db.Column(db.Boolean, default = False)

    def __init__(self, title, description, checklist_item, due_date, completed):
        self.title = title
        self.description = description
        self.checklist_item = checklist_item
        self.due_date = due_date
        self.completed = completed

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String(100), nullable = False)
    password = db.Column(db.String(50), nullable = False)

    def __init__(self, user, email, password):
        self.user = user
        self.email = email
        self.password = password

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # remove all entries in the database
    '''
    for task in Task.query.all():
        Task.query.delete()
    db.session.commit()
    '''    
    return render_template('index.html', tasks = Task.query.all())

@app.route('/home')
def home():
    return render_template('home.html', tasks = Task.query.all())

@app.route('/add-task', methods = ["GET", "POST"])
def add_task():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"] # else None
        checklist_item = request.form["checklist_item"] # else None
        due_date = request.form["due_date"] # else None # prints as YYYY-MM-DD
        if type(due_date) is str:
            due_date = datetime.strptime(due_date, '%Y-%m-%d')

        new_task = Task(title = title, description = description, checklist_item = checklist_item, due_date = due_date, completed = False)
        db.session.add(new_task)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('add_task.html')

@app.route("/view")
def view():
    return render_template("view.html", values=Task.query.all())


@app.route("/login", methods = ["GET", "POST"]) # issue with "user() getting an unexpected keyword argument 'user'"
def login():
    user = None
    if request.method == "POST":
        session.permanent = True
        user = request.form["username"]
        session["user"] = user
        return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/sign-up", methods = ["GET", "POST"]) # issue with "user() getting an unexpected keyword argument 'user'"
def signup():
    if request.method == "POST":
        email = request.form["inputEmail"]
        user = request.form["username"]
        password = request.form["inputPassword"]
        new_user = User(user = user, email = email, password = password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("user"))
    return render_template("signup.html")

@app.route("/<user>")
def user():
    if "user" in session:
        user = session["user"]
        return render_template("user.html")
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        flash("You have been logged out.", "info")
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)