from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime

db = SQLAlchemy()

friends = db.Table('friends',
    db.Column('user_id', db.String(36), db.ForeignKey('User.id'), primary_key = True),
    db.Column('friend_id', db.String(36), db.ForeignKey('User.id'), primary_key = True),
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

    def decline_friend_request(self, user):
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