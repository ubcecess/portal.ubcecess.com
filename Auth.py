#!/usr/local/bin/python
from flask import Flask, session, redirect, url_for, request, render_template
from flask_oauthlib.client import OAuth
from pony.orm import *
import json

app = Flask(__name__)

# Configuration
# config should contain:
#   GOOGLE_ID
#   GOOGLE_SECRET
#   DEBUG = (T/F)
#   SECRET_KEY

app.config.from_object('config')
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
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

# Database + ORM

db = Database('sqlite', 'testdb', create_db=True)

class Users(db.Entity):
    name = Required(str)
    email = Required(str)
    role = Required(str)

'''
class Docs(db.Entity):
    name = Required(str)
    url = Required(str)
    kind = Required(str)
'''

db.generate_mapping(create_tables=True)

@app.route('/')
def index():
    if session.get('google_token'):
        userinfo = google.get('userinfo')
        googleData = json.loads(userinfo.__dict__['raw_data'])
        with db_session:
            for user in select(user for user in Users):
                try:
                    if  googleData['email'] == user.email:
                        return render_template('index.html', inDB=True, name=user.name)
                    else:
                        return render_template('index.html', inDB=False)
                except KeyError:
                    return render_template('index.html', inDB=False)
            return "hello"
    return render_template('index.html')


@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None:
        return 'Access Denied: reason is %s error is %s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (response['access_token'], '')
    return redirect(url_for('index'))

@google.tokengetter
def get_google_auth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run()

