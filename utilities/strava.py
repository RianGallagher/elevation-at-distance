import requests
import os
import json
from flask import session

STRAVA_API_URL = "https://www.strava.com/api/v3"


def request_route_gpx(route_id):
    # bearer_token = os.environ.get('STRAVA_TOKEN')
    bearer_token = session['strava_token']
    print(f"bearer_token: {bearer_token}")
    url = f"{STRAVA_API_URL}/routes/{route_id}/export_gpx"
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    response = requests.request("GET", url, headers=headers)
    return response.text


def request_route(route_id):
    # bearer_token = os.environ.get('STRAVA_TOKEN')
    bearer_token = session['strava_token']
    url = f"{STRAVA_API_URL}/routes/{route_id}"
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text)
