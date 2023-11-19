from flask import Flask, request, session, render_template
from flask_session import Session
from flask_cors import CORS
import os
from dotenv import load_dotenv
import gpxpy.gpx
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
Session(app)


@app.route("/")
def render_home():
    return render_template('index.html')


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
