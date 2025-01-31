import logging
from datetime import datetime

import pytz
import requests
from flask import Flask, render_template, request, jsonify
from flask_restx import Api, Resource, fields

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Flask-RestX
api = Api(app, version='1.0', title='Weather API',
    description='A simple weather API with city temperature information',
    doc='/api')

# Define namespaces
ns = api.namespace('weather', description='Weather operations')

# Define models
weather_model = api.model('Weather', {
    'temperature': fields.Float(description='Temperature value'),
    'unit': fields.String(description='Temperature unit (°F or °C)'),
    'local_time': fields.String(description='Local time at location')
})

location_parser = api.parser()
location_parser.add_argument('lat', type=float, required=True, help='Latitude')
location_parser.add_argument('lon', type=float, required=True, help='Longitude')
location_parser.add_argument('unit', type=str, required=True, help='Temperature unit (fahrenheit/celsius)')

_TEMP_UNITS = ["fahrenheit", "celsius"]
_CITIESCITIES = {
    "Phoenix, AZ": {"lat": 33.4484, "lon": -112.0740, "default_unit": "fahrenheit", "timezone": "America/Phoenix"},
    "Seattle, WA": {"lat": 47.6062, "lon": -122.3321, "default_unit": "celsius", "timezone": "America/Los_Angeles"},
    "New York, NY": {"lat": 40.7128, "lon": -74.0060, "default_unit": "fahrenheit", "timezone": "America/New_York"},
    "Miami, FL": {"lat": 25.7617, "lon": -80.1918, "default_unit": "fahrenheit", "timezone": "America/New_York"},
    "Anchorage, AK": {"lat": 61.2181, "lon": -149.9003, "default_unit": "fahrenheit", "timezone": "America/Anchorage"},
    "Charlotte, NC": {"lat": 35.2271, "lon": -80.8431, "default_unit": "fahrenheit", "timezone": "America/New_York"},
    "Vancouver, BC": {"lat": 49.2827, "lon": -123.1207, "default_unit": "celsius", "timezone": "America/Vancouver"},
    "Tokyo, Japan": {"lat": 35.6762, "lon": 139.6503, "default_unit": "celsius", "timezone": "Asia/Tokyo"}
}

def guess_tz(lon: float) -> pytz.timezone:
    """
    Calculate timezone from longitude coordinate
    """
    utc_offset: int = round(lon / 15)
    tz_name: str = f"Etc/GMT{'+' if utc_offset < 0 else '-'}{abs(utc_offset)}" if utc_offset else "Etc/GMT"
    return pytz.timezone(tz_name)

def get_weather_data(lat: float, lon: float, unit: str, city: str = None) -> dict:
    """
    Get real weather data from Open-Meteo API with correct local time.
    """
    unit = unit.lower()
    if unit not in _TEMP_UNITS:
        logger.warning(f'Temperature unit "{unit}" is not supported. Using celsius instead.')
    logger.info(f'Getting weather for lat:{lat}, lon:{lon}, unit:{unit}, city:{city}')

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "temperature_unit": unit,
        "current": "temperature_2m",
        "timezone": _CITIESCITIES[city]["timezone"] if city in _CITIESCITIES else "auto"
    }

    response = requests.get(url, params=params)
    data = response.json()

    tz = pytz.timezone(_CITIESCITIES[city]["timezone"]) if city in _CITIESCITIES else guess_tz(lon)
    local_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')

    return {
        'temperature': data['current']['temperature_2m'],
        'unit': '°F' if unit == 'fahrenheit' else '°C',
        'local_time': local_time
    }

# HTML interface route
@app.route('/cities')
def index():
    logger.info('Loading index page')
    return render_template('index.html', cities=_CITIESCITIES)

# API routes with Swagger
@ns.route('/')
class WeatherResource(Resource):
    @ns.doc('get_weather')
    @ns.expect(location_parser)
    @ns.marshal_with(weather_model)
    def get(self):
        args = location_parser.parse_args()
        return get_weather_data(args['lat'], args['lon'], args['unit'])

if __name__ == '__main__':
    logger.info('Starting Weather App')
    app.run(host='0.0.0.0', port=5000)
