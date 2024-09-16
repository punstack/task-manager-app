from flask import render_template, redirect, request, url_for, session, flash
from models import User, db

def create_users():
    # prevents any user from using the name of a route as their username
    setting_user = User(user = "settings", email = "000", password = " ")
    db.session.add(setting_user)
    add_task_user = User(user = "add-task", email = "001", password = " ")
    db.session.add(add_task_user)
    archive_user = User(user = "archive", email = "010", password = " ")
    db.session.add(archive_user)
    search_user = User(user = "search", email = "011", password = " ")
    db.session.add(search_user)
    sign_up_user = User(user = "sign-up", email = "100", password = " ")
    db.session.add(sign_up_user)
    login_user = User(user = "login", email = "101", password = " ")
    db.session.add(login_user)
    user_user = User(user = "user", email = "110", password = " ")
    db.session.add(user_user)
    
    db.session.commit()

'''
INSERT INTO User (username, email, password) VALUES ('settings', 'reserved@domain.com', 'reserved');
INSERT INTO user (username, email, password) VALUES ('add-task', 'reserved@domain.com', 'reserved');
INSERT INTO user (username, email, password) VALUES ('archive', 'reserved@domain.com', 'reserved');
INSERT INTO user (username, email, password) VALUES ('search', 'reserved@domain.com', 'reserved');
INSERT INTO user (username, email, password) VALUES ('sign-up', 'reserved@domain.com', 'reserved');
INSERT INTO user (username, email, password) VALUES ('login', 'reserved@domain.com', 'reserved');
INSERT INTO user (username, email, password) VALUES ('user', 'reserved@domain.com', 'reserved');
'''

def search_tasks(query):
    if query:
        results = User.query.filter(
            (User.user.ilike(f'%{query}%'))
        ).all()
    else:
        results = []
    return results

def delete_status(user):
    try:
        delete_status = request.form["delete_status"]

        if delete_status == "-1": # delete account
            try:
                db.session.delete(user)
                db.session.commit()
                session.pop("user", None)
                flash("Your account has been deleted. Please log in again.", "error")
                return redirect(url_for("view_user.login"))
            except Exception as e:
                db.session.rollback()  
                flash(f"An error occured while trying to delete the account: {str(e)}", "error")
                return redirect(url_for("view_task.settings"))
    except:
        return render_template("settings.html", email=user.email, user=session["user"])
    
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