import logging
from datetime import datetime

import pytz
import requests
from flask import Flask, render_template
from flask_restx import Api, Resource, fields
from openai import OpenAI

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
_CITIES = {
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


def _call_open_meteo_api(lat: float, lon: float, unit: str, city: str = None, **params) -> dict:
    """
    Common routine to call Open-Meteo API with validated parameters.
    """
    unit = unit.lower()
    if unit not in _TEMP_UNITS:
        logger.warning(f'Temperature unit "{unit}" is not supported. Using celsius instead.')

    logger.info(f'Calling Open-Meteo API for lat:{lat}, lon:{lon}, unit:{unit}, city:{city}')

    base_params = {
        "latitude": lat,
        "longitude": lon,
        "temperature_unit": unit,
        "timezone": _CITIES[city]["timezone"] if city in _CITIES else "auto"
    }

    # Merge base parameters with additional params
    request_params = {**base_params, **params}

    url = "https://api.open-meteo.com/v1/forecast"
    response = requests.get(url, params=request_params)
    return response.json()


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate latitude and longitude bounds
    """
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0

def get_weather_data(lat: float, lon: float, unit: str, city: str = None) -> dict:
    """
    Get current weather data from Open-Meteo API.
    """
    if not validate_coordinates(lat, lon):
        raise ValueError("Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180")

    data = _call_open_meteo_api(
        lat=lat,
        lon=lon,
        unit=unit,
        city=city,
        current="temperature_2m"
    )
    tz = pytz.timezone(_CITIES[city]["timezone"]) if city in _CITIES else guess_tz(lon)
    local_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')

    return {
        'temperature': data['current']['temperature_2m'],
        'unit': '°F' if unit.lower() == 'fahrenheit' else '°C',
        'local_time': local_time
    }


def get_weather_forecast(lat: float, lon: float, unit: str, city: str = None) -> dict:
    """
    Get weather forecast data from Open-Meteo API.
    """
    data = _call_open_meteo_api(
        lat=lat,
        lon=lon,
        unit=unit,
        city=city,
        hourly=["temperature_2m", "precipitation_probability", "weathercode"],
        daily=["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        forecast_days=3
    )

    # Get current hour index
    tz = pytz.timezone(_CITIES[city]["timezone"]) if city in _CITIES else guess_tz(lon)
    current_hour = datetime.now(tz).hour

    # Create hourly forecast starting from current hour
    hourly_forecast = [
        {
            "time": data['hourly']['time'][i],
            "temp": data['hourly']['temperature_2m'][i],
            "precipitation_prob": data['hourly']['precipitation_probability'][i],
            "weather_desc": get_weather_description(data['hourly']['weathercode'][i])
        }
        for i in range(current_hour, current_hour + 24)
    ]

    # Rest of the code remains the same
    daily_forecast = [
        {
            "date": data['daily']['time'][i],
            "temp_max": data['daily']['temperature_2m_max'][i],
            "temp_min": data['daily']['temperature_2m_min'][i],
            "precipitation_sum": data['daily']['precipitation_sum'][i]
        }
        for i in range(3)
    ]

    return {
        "hourly": hourly_forecast,
        "daily": daily_forecast,
        "unit": '°F' if unit.lower() == 'fahrenheit' else '°C'
    }


def get_weather_description(code: int) -> str:
    """Convert weather code to human-readable description."""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        95: "Thunderstorm"
    }
    return weather_codes.get(code, "Unknown")


# HTML interface route
@app.route('/cities')
def index():
    logger.info('Loading index page')
    return render_template('index.html', cities=_CITIES)


# API routes with Swagger
@ns.route('/')
class WeatherResource(Resource):
    @ns.doc('get_weather')
    @ns.expect(location_parser)
    @ns.marshal_with(weather_model)
    def get(self):
        args = location_parser.parse_args()
        if not validate_coordinates(args['lat'], args['lon']):
            api.abort(400, "Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180")
        return get_weather_data(args['lat'], args['lon'], args['unit'])


# Add new route in the API section
def transform_forecast_with_llm(forecast_data: dict, city: str = None) -> str:
    """
    Transform weather forecast data into natural language using GPT-3.5-turbo
    """
    client = OpenAI(api_key='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')

    # Format the weather data into a readable string
    weather_info = []
    for day in forecast_data['daily']:
        weather_info.append(
            f"Date: {day['date']}, "
            f"High: {day['temp_max']}{forecast_data['unit']}, "
            f"Low: {day['temp_min']}{forecast_data['unit']}, "
            f"Precipitation: {day['precipitation_sum']}mm"
        )

    weather_data = "\n".join(weather_info)
    location = f" for {city}" if city else ""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a friendly meteorologist creating an engaging weather forecast"
            },
            {
                "role": "user",
                "content": f"Please transform this weather data{location} into a conversational easy to understand narrative:\n{weather_data}"
            }
        ]
    )

    return response.choices[0].message.content

@ns.route('/forecast')
class WeatherForecastResource(Resource):
    @ns.doc('get_forecast')
    @ns.expect(location_parser)
    def get(self):
        args = location_parser.parse_args()
        forecast_data = get_weather_forecast(args['lat'], args['lon'], args['unit'])

        # Get city name if coordinates match a known city
        city = next((city for city, data in _CITIES.items()
                    if data['lat'] == args['lat'] and data['lon'] == args['lon']), None)

        forecast_data['narrative'] = transform_forecast_with_llm(forecast_data, city)
        return forecast_data

if __name__ == '__main__':
    logger.info('Starting Weather App')
    app.run(host='0.0.0.0', port=5000)
