from flask import Flask, request, session, render_template, current_app, abort, url_for, redirect, flash
from flask_session import Session
from flask_cors import CORS
import os
import secrets
import requests
from dotenv import load_dotenv
import gpxpy.gpx
from urllib.parse import urlencode
from utilities.find_closet_entry import find_closest_entry
from utilities.format_gpx import format_gpx
from utilities.strava import request_route_gpx, request_route
from utilities.create_chart import create_chart


load_dotenv()

app = Flask(__name__)

CORS(app)

SECRET_KEY = os.environ.get('FLASK_SESSION_SECRET_KEY')
SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
app.config['OAUTH2_PROVIDERS'] = {
    # Google OAuth 2.0 documentation:
    # https://developers.google.com/identity/protocols/oauth2/web-server#httprest
    'strava': {
        'client_id': os.environ.get('STRAVA_CLIENT_ID'),
        'client_secret': os.environ.get('STRAVA_CLIENT_SECRET'),
        'authorize_url': 'https://www.strava.com/oauth/authorize',
        'token_url': 'https://www.strava.com/oauth/token',
        'scopes': ['read_all'],
    },
}
Session(app)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/authorize')
def oauth2_authorize():
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get('strava')
    if provider_data is None:
        abort(404)

    # generate a random string for the state parameter
    session['oauth2_state'] = secrets.token_urlsafe(16)

    # create a query string with all the OAuth2 parameters
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('oauth2_callback', _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    # redirect the user to the OAuth2 provider authorization URL
    return redirect(provider_data['authorize_url'] + '?' + qs)


@app.route('/callback')
def oauth2_callback():
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get('strava')
    if provider_data is None:
        abort(404)

    # if there was an authentication error, flash the error messages and exit
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('index'))

    # make sure that the state parameter matches the one we created in the
    # authorization request
    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    # make sure that the authorization code is present
    if 'code' not in request.args:
        abort(401)

    # exchange the authorization code for an access token
    response = requests.post(provider_data['token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('oauth2_callback', _external=True),
    }, headers={'Accept': 'application/json'})

    if response.status_code != 200:
        abort(401)

    json_response = response.json()
    oauth2_token = json_response.get('access_token')

    session['strava_token'] = oauth2_token

    if not oauth2_token:
        abort(401)

    return redirect(url_for('index'))


@app.route("/route")
def get_route():
    route_id = request.args.get('stravaId')

    route = request_route(route_id)
    route_name = route["name"]
    route_distance = round(route["distance"] / 1000, 2)
    route_elevation_gain = round(route["elevation_gain"], 2)

    raw_route_gpx = request_route_gpx(route_id)
    gpx = gpxpy.parse(raw_route_gpx)
    formatted_gpx = format_gpx(gpx)

    chart_html = create_chart(formatted_gpx)

    session["gpx"] = formatted_gpx

    return render_template('route.html', route_chart=chart_html, route_name=route_name, route_distance=route_distance, route_elevation_gain=route_elevation_gain)


@app.route("/elevation-at-distance")
def get_elevation_at_distance():
    raw_distance = request.args.get('distance')
    if raw_distance is None:
        return "<p>Distance is required</p>"
    distance = float(raw_distance)
    gpx = session.get("gpx", 'not set')
    if isinstance(gpx, list):
        closest_entry = find_closest_entry(gpx, distance)
        closest_distance = round(closest_entry['distance'], 2)
        final_elevation = round(closest_entry['elevation_gain'], 2)

        return render_template('elevation-info.html', closest_distance=closest_distance, final_elevation=final_elevation)
    return "<p>GPX data is required</p>"
