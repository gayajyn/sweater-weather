from PyQt5 import QtCore
import requests


class WeatherWorker(QtCore.QThread):
    weather_fetched = QtCore.pyqtSignal(str)

    def __init__(self, latitude, longitude):
        super().__init__()
        self.latitude = latitude
        self.longitude = longitude

    def run(self):
        self.weather_info = self.get_weather_data()
        self.weather_fetched.emit(self.weather_info)

    def get_weather_data(self):
        # Get grid points based on latitude and longitude
        url = f"https://api.weather.gov/points/{self.latitude},{self.longitude}"
        response = requests.get(url)
        if response.status_code != 200:
            return "Error fetching grid points."

        grid_data = response.json()
        forecast_url = grid_data['properties']['forecast']

        # Fetch weather forecast data from the NWS API
        response = requests.get(forecast_url)
        if response.status_code != 200:
            return "Could not retrieve weather data."

        forecast_data = response.json()
        periods = forecast_data['properties']['periods']
        
        # Retrieve temperature and wind speed from the first forecast period
        temp = periods[0]['temperature']
        wind_speed = periods[0]['windSpeed']
        return f"Temperature: {temp}°F, Wind: {wind_speed}"