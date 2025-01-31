# Weather API

Dockerized weather API in Python

## Overview

Dockerized weather API wrapper for open-meteo.com built with Python and Flask.

## Features

- Real-time weather data from open-meteo.com
- Current temperature at 2m above ground
- Local time display for each location
- Supports both Celsius and Fahrenheit
- Pre-configured cities:
  - Phoenix, AZ (default)
  - Charlotte, NC
  - Vancouver, BC
  - Tokyo, Japan
- 
You can also specify your own location by entering the latitude and longitude, for example:
  - None of the above (Berlin coordinates)

## Quick Start
You can access the weather service through three different interfaces:

### 1. Web Interface
The web interface is available at `http://localhost:5000/cities` when running the container. It provides a user-friendly way to select cities or enter custom coordinates.

### 2. REST API Endpoint
Access weather data directly via HTTP GET requests:
```json
GET http://localhost:5000/weather?lat=33.4484&lon=-112.0740&unit=fahrenheit

Response:
{
  "local_time": "2025-01-30 18:09:48",
  "temperature": 52.9,
  "unit": "°F"
}
```

### 3. Swagger UI
Interactive API documentation is available at http://localhost:5000/api/. 

This interface allows you to:

- Explore available endpoints
- Test API calls directly from the browser
- View request/response schemas
- Try out different parameters

# Build the Docker container:
```bash
docker build -t weather-app .
## Features

- Retrieve current weather data for a given location
- Support for multiple weather data providers
- Caching mechanism for improved performance
- RESTful API design

## Setup Instructions

1. Clone the repository:
   
   git clone https://github.com/sourcegraph/weather-api.git
   cd weather-api

2. Build the Docker image:
   
   docker build -t weather-api .
   

3. Run the container:
   
   docker run -p 5000:5000 weather-app
   
```

The API will be available at `http://localhost:5000`.

## API Documentation

### Get Current Weather

Endpoint: `/weather`

Method: `GET`

Query Parameters:
- `location` (required): City name or coordinates (latitude,longitude)
- `unit` (optional): 'celsius' or 'fahrenheit' (default: 'celsius')

Example Request:

GET /weather?location=London&units=metric


Example Response:

{
  "location": "London",
  "temperature": 15.5,
  "humidity": 76,
  "wind_speed": 3.6,
  "description": "Partly cloudy"
}


## Development Guidelines

1. Follow PEP 8 style guide for Python code.
2. Write unit tests for new features and bug fixes.
3. Use meaningful commit messages and create pull requests for review.
4. Update documentation when adding or modifying features.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
