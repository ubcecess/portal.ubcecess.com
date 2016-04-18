#!/usr/bin/python
from flask_oauthlib.client import OAuth
import config

info = config.info
# Setup Oauth for Google

oauth = OAuth()
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
