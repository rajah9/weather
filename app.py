import logging
from datetime import datetime

import requests
from flask import Flask, render_template, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

CITIES = {
    "Phoenix, AZ": {"lat": 33.4484, "lon": -112.0740, "default_unit": "fahrenheit"},
    "Seattle, WA": {"lat": 47.6062, "lon": -122.3321, "default_unit": "celsius"},
    "New York, NY": {"lat": 40.7128, "lon": -74.0060, "default_unit": "fahrenheit"},
    "Miami, FL": {"lat": 25.7617, "lon": -80.1918, "default_unit": "fahrenheit"},
    "Anchorage, AK": {"lat": 61.2181, "lon": -149.9003, "default_unit": "fahrenheit"},
    "Charlotte, NC": {"lat": 35.2271, "lon": -80.8431, "default_unit": "fahrenheit"},
    "Vancouver, BC": {"lat": 49.2827, "lon": -123.1207, "default_unit": "celsius"},
    "Tokyo, Japan": {"lat": 35.6762, "lon": 139.6503, "default_unit": "celsius"}
}


def get_weather_data(lat, lon, unit):
    """Get real weather data from Open-Meteo API"""
    logger.info(f'Getting weather for lat:{lat}, lon:{lon}, unit:{unit}')

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "temperature_unit": "fahrenheit" if unit == "fahrenheit" else "celsius",
        "current": "temperature_2m",
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    data = response.json()

    return {
        'temperature': data['current']['temperature_2m'],
        'unit': '°F' if unit == 'fahrenheit' else '°C',
        'local_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
@app.route('/')
def index():
    logger.info('Loading index page')
    return render_template('index.html', cities=CITIES)


@app.route('/weather')
def weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    unit = request.args.get('unit')
    logger.info(f'Weather request received - lat:{lat}, lon:{lon}, unit:{unit}')

    weather_data = get_weather_data(lat, lon, unit)
    logger.info(f'Returning weather data: {weather_data}')
    return jsonify(weather_data)


if __name__ == '__main__':
    logger.info('Starting Weather App')
    app.run(host='0.0.0.0', port=5000)
