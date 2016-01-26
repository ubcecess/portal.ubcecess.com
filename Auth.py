from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
import config
import sqlite3
import json


from werkzeug.debug import DebuggedApplication



app = Flask(__name__)

dapp = DebuggedApplication(app, evalex=True) 

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


@app.route('/')
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        # return jsonify({"data": me.data})
        data = json.loads(me.__dict__['raw_data'])
        return data['email']
       
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    #return jsonify({"data": me.data})
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    emails = c.execute("SELECT EmailAddress FROM userinfo")
    data = json.loads(me.__dict__['raw_data'])
    return data['email']

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


if __name__ == '__main__':
    app.run()
