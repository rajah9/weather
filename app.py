import ssl
import certifi
from OpenSSL import SSL
from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import pytz


app = Flask(__name__)

CITIES = {
    "Phoenix, AZ": {"lat": 33.4484, "lon": -112.0740, "default_unit": "fahrenheit", "timezone": "America/Phoenix"},
    "Charlotte, NC": {"lat": 35.2271, "lon": -80.8431, "default_unit": "fahrenheit", "timezone": "America/New_York"},
    "Vancouver, BC": {"lat": 49.2827, "lon": -123.1207, "default_unit": "celsius", "timezone": "America/Vancouver"},
    "Tokyo, Japan": {"lat": 35.6762, "lon": 139.6503, "default_unit": "celsius", "timezone": "Asia/Tokyo"},
    "None of the above": {"lat": 52.52, "lon": 13.41, "default_unit": "celsius", "timezone": "Europe/Berlin"}
}


@app.route('/')
def index():
    return render_template('index.html', cities=CITIES)


@app.route('/weather', methods=['GET'])
def get_weather():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    unit = request.args.get('unit', 'celsius')

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}¤t=temperature_2m"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data['current']['temperature_2m']

        if unit == 'fahrenheit':
            temp = (temp * 9 / 5) + 32

        # Get local time for the coordinates
        timezone = pytz.timezone(next(
            (city['timezone'] for city in CITIES.values()
             if city['lat'] == lat and city['lon'] == lon),
            'UTC'
        ))
        local_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S %Z')

        return jsonify({
            'temperature': round(temp, 1),
            'unit': '°F' if unit == 'fahrenheit' else '°C',
            'local_time': local_time
        })

    return jsonify({'error': 'Failed to fetch weather data'}), 500
if __name__ == '__main__':
    # Configure SSL context
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    app.run(host='0.0.0.0', port=5000)




