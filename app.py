from flask import Flask
from flask_migrate import Migrate
from datetime import timedelta
from dotenv import load_dotenv
import os
from view_user import view_user
from view_task import view_task
from models import db
from functions import create_users

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_key_for_dev')
app.permanent_session_lifetime = timedelta(days=1)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(view_user, url_prefix = '')
app.register_blueprint(view_task, url_prefix = '')

with app.app_context():
    #db.drop_all() # drop all tables
    db.create_all() # create tables based on models
    create_users()

if __name__ == '__main__':
    app.run(debug=False)