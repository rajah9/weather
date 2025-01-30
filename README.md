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
  - None of the above (Berlin coordinates)

## Quick Start

Build the Docker container:
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
   
   docker run -p 8000:8000 weather-api
   

The API will be available at `http://localhost:8000`.

## API Documentation

### Get Current Weather

Endpoint: `/weather`

Method: `GET`

Query Parameters:
- `location` (required): City name or coordinates (latitude,longitude)
- `units` (optional): 'metric' or 'imperial' (default: 'metric')

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
