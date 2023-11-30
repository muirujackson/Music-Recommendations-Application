from flask import session, redirect, url_for
from dotenv import load_dotenv
import os
import requests
from functools import wraps
from datetime import datetime, timedelta


# Load environment variables from .env
load_dotenv()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def refresh_token():
    refresh_session_token = session.get('refresh_token')  # Retrieve the refresh token from the session
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_session_token,
        'client_id': os.environ.get('CLIENT_ID'),
        'client_secret': os.environ.get('CLIENT_SECRET')
    }
    response = requests.post(os.environ.get('TOKEN_URL'), data=payload)
    new_access_token = response.json().get('access_token')
    # Update the session with the new access token
    session['access_token'] = new_access_token


def check_session_validity(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'access_token' not in session or session_expired():
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


def session_expired():
    last_activity_time = session.get('last_activity_time')
    if last_activity_time and (datetime.now() - last_activity_time > timedelta(minutes=1)):
        return True
    return False
