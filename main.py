#!/usr/local/bin/python
from flask import Flask, session, redirect, url_for, request, render_template
from flask_oauthlib.client import OAuth
from pony.orm import *
import json
import os.path


app = Flask(__name__)

# Configuration
# infoo.json should contain:
#   GOOGLE_ID
#   GOOGLE_SECRET
#   SECRET_KEY

if not os.path.isfile('info.json'):
    print "Please provide the following information. This will be saved in info.json \
    and used for future requests"

    infoIn = {'consumer_key' : raw_input("Google Consumer Key: "), \
            'consumer_secret' : raw_input("Google Consumer Key: "), \
            'secret_key' : raw_input("App Secret Key: ")}

    with open('info.json', 'w') as outfile:
        json.dump(infoIn, outfile)

with open('info.json', 'r') as infile:
    global info
    info = json.load(infile)

# Setup Oauth for Google

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=info['consumer_key'],
    consumer_secret=info['consumer_secret'],
    request_token_params={
        'scope': 'email',
        'access_type':'offline'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Provide app a secret key for sessions module
app.secret_key = info['secret_key']

# Database + ORM

db = Database('sqlite', 'testdb', create_db=True)

class Users(db.Entity):
    name = Required(str)
    email = Required(str)
    role = Required(str)

db.generate_mapping(create_tables=True)

@app.route('/')
def index():
    if session.get('userinfo'):
        return render_template('index.html', logged_in='true', name=session.get('userinfo').get('name'))        
    return render_template('index.html', logged_in='false')

@app.route('/drive')
def drive():
    return render_template('drive.html', client_id=info['consumer_key'])

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    session.pop('userinfo', None)
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
    google_userinfo = google.get('userinfo').data
    
    with db_session:
        if exists(user for user in Users if user.email == google_userinfo.get('email')):
            session['userinfo'] = google_userinfo
            session.permanent = True
            return redirect(url_for('index'))
        else:
            session.pop('google_token', None)
            return "Sorry, you'll need to register"
            

@google.tokengetter
def get_google_auth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True)

