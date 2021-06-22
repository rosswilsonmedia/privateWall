from flask_app import app
from datetime import datetime

from ..models.user import User

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

from flask import render_template, redirect, request, session, flash

@app.route('/')
def index():
    if 'id' in session:
        return redirect('/wall')

    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    user_in_db=User.get_by_email({'email':request.form['email']})
    if not user_in_db:
        flash("*invalid email address", "login_errors")
        return redirect('/')

    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("*password incorrect", "login_errors")
        return redirect('/')

    session['id']=user_in_db.id
    return redirect('/wall')

@app.route('/register', methods=['POST'])
def register():
    data={
        'first_name':request.form['first_name'],
        'last_name':request.form['last_name'],
        'email':request.form['email'],
        'password':request.form['password'],
        'confirm_password':request.form['confirm_password']
    }
    if not User.validate(data):
        return redirect('/')
    data['password']=bcrypt.generate_password_hash(data['password'])
    del data['confirm_password']
    print(data)
    user_id=User.create(data)
    session['id']=user_id
    return redirect('/wall')

@app.route('/wall')
def wall():
    if 'id' not in session:
        return redirect('/')

    data={
        'id':session['id']
    }
    logged_in_user=User.get_one(data)
    all_users_except=User.get_all_except(data)

    now=datetime.now()
    return render_template('wall.html', user=logged_in_user, all_users_except=all_users_except, now=now)

@app.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out', 'logout')
    return redirect('/')