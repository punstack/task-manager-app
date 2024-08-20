# python -m venv .venv
# source  .venv/Scripts/activate

from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db' # "tasks" table
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(200), nullable = True, default = None)
    checklist_item = db.Column(db.String(100), nullable = True, default = None)
    due_date = db.Column(db.DateTime, nullable = True, default = None)
    completed = db.Column(db.Boolean, default = False)

    def __init__(self, title):
        self.title = title
        self.description = description
        self.checklist_item = checklist_item
        self.due_date = due_date
        self.completed = completed


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-task') #methods = GET, POST
def add_task():
    return render_template('add_task.html')


if __name__ == '__main__':
    '''
    db.create_all()
    
    new_task = Task(title="Sample Task", description="This is a task")
    db.session.add(new_task)
    db.session.commit()
    
    tasks = Task.query.all()

    task = Task.query.get(task_id)
    task.completed = True
    db.session.commit()

    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    '''
    app.run() #debug=True



    '''
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_task = Task(title=title, description=description)
        db.session.add(new_task)
        db.session.commit()
        return redirect('/')
    '''