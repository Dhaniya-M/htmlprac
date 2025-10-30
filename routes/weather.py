from flask import Blueprint, current_app
from flask_jwt_extended import jwt_required
from utils.helpers import json_response
import datetime

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/weather/current', methods=['GET'])
@jwt_required()
def current_weather():
    # Mock current weather data; replace with real API calls later
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    data = {
        'location': 'Demo Farm',
        'timestamp': now,
        'temperature': 28 + (datetime.datetime.utcnow().second % 8),
        'humidity': 60 + (datetime.datetime.utcnow().second % 20),
        'wind_speed': 5 + (datetime.datetime.utcnow().second % 15),
        'alerts': []
    }
    return json_response('success', 'Weather fetched', {'weather': data})


@weather_bp.route('/weather/forecast', methods=['GET'])
@jwt_required()
def weather_forecast():
    # Mock 5-day forecast
    base = datetime.date.today()
    forecast = []
    for i in range(5):
        day = base + datetime.timedelta(days=i)
        forecast.append({
            'date': day.isoformat(),
            'temperature': 25 + (i * 1.5),
            'humidity': 60 + i,
            'wind_speed': 5 + i,
            'conditions': ['Sunny', 'Partly Cloudy', 'Cloudy', 'Rainy', 'Thunderstorms'][i % 5]
        })
    return json_response('success', 'Forecast fetched', {'forecast': forecast})
