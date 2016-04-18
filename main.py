#!/usr/local/bin/python
from flask import Flask, session, redirect, url_for, request, render_template
from flask_oauthlib.client import OAuth
from pony.orm import *

# App Specific Modules
from config import *
from oauth import *
from db import *

app = Flask(__name__)

# For sessions module
app.secret_key = info['secret_key']


@app.route('/')
def index():
    if session.get('logged_in'):
        return render_template('index.html', logged_in='true', name=session.get('name'))
    return render_template('index.html', logged_in='false')

@app.route('/drive')
def drive():
    docs =  Docs.select()[:]
    return render_template('drive.html', client_id= info['consumer_key'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    name = session.get('name','')
    email = session.get('email','')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        with db_session:
            newuser = Users(name=name,email=email,group='unconfirmed' )
        return "registered"

    session.clear()
    return render_template('register.html', name = name,email = email)

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        if session.get('email'):
            with db_session:
                if get(u.group for u in Users if u.email == \
                        session.get('email')) == 'Admin':
                    user_id = request.form['id']
                    param = request.form['param']
                    val = request.form['val']
                    update = {param: val}
                    Users[user_id].set(**update)

                    return "done"
    if session.get('email'):
        with db_session:
            if get(u.group for u in Users if u.email == \
                    session.get('email')) == 'Admin':
                users =  Users.select()[:]
                return render_template('confirm.html', users=users)



@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/login/authorized')
@google.authorized_handler
def authorized(response):
    if response is None:
        return 'Access Denied: reason is %s error is %s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (response['access_token'],)
    google_info = google.get('userinfo').data

    with db_session:
        if exists(user for user in Users if user.email == google_info.get('email')):
            user = get(u for u in Users if u.email== google_info.get('email'))

            if user.group == 'unconfirmed':
                return "You'll need to get confirmed from an admin"
            session['google_token'] = (response['access_token'],)
            session['logged_in'] = True
            session['name'] = user.name
            session['email'] = user.email
            session.permanent = True
            return redirect(url_for('index'))
        else:
            session['name'] = google_info.get('name')
            session['email'] = google_info.get('email')
            session.pop('google_token', None)
            return redirect(url_for('register'))

@google.tokengetter
def get_google_auth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True)
