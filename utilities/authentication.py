from requests import Response
from flask import session
from datetime import datetime


def save_authentication_details(response: Response):
    json_response = response.json()
    oauth2_token = json_response.get('access_token')
    refresh_token = json_response.get('refresh_token')
    expires_at = json_response.get('expires_at')

    session['strava_token'] = oauth2_token
    session['expires_at'] = expires_at
    session['refresh_token'] = refresh_token


def is_token_expired():
    if 'expires_at' not in session:
        return False
    current_timestamp = datetime.utcnow().timestamp()
    if session['expires_at'] > current_timestamp:
        return False

    return True
