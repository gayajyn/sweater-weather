from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from ui_mainwindow import Ui_MainWindow
from weatherworker import WeatherWorker


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.weather_button.clicked.connect(self.fetch_weather)
        self.ui.check_weather_button.clicked.connect(self.check_ideal_weather)

    def fetch_weather(self):
        self.weather_worker = WeatherWorker(32.96, -96.73)  # Latitude and Longitude for Richardson
        self.weather_worker.weather_fetched.connect(self.update_weather_info)
        self.weather_worker.start()  # Start the worker thread

    def update_weather_info(self, weather_info):
        self.ui.status_label.setText(weather_info)

    def check_ideal_weather(self):
        self.weather_worker = WeatherWorker(32.96, -96.73)
        self.weather_worker.weather_fetched.connect(self.compare_weather)
        self.weather_worker.start()

    def compare_weather(self, current_weather):
        try:
            # Get ideal values from input fields
            ideal_temp = float(self.ui.ideal_temp_input.text())
            ideal_wind = float(self.ui.ideal_wind_input.text())
          
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric values for ideal weather.")
            return
        # Check current weather
        current_data = current_weather.split(", ")
        current_temp = float(current_data[0].split(": ")[1][:-2])  # Extract temperature
        current_wind = float(current_data[1].split(": ")[1].split(" ")[0])  # Extract wind speed

        # Check if current conditions match ideal conditions
        temp_match = ideal_temp - 5 <= current_temp <= ideal_temp + 5
        wind_match = ideal_wind - 5 <= current_wind <= ideal_wind + 5

        # Feedback on temperature comparison
        if not temp_match:
            if current_temp > ideal_temp + 5:
                temp_feedback = f"Too hot! Current Temp: {current_temp}°F."
            else:
                temp_feedback = f"Too cold! Current Temp: {current_temp}°F."
        else:
            temp_feedback = f"Temperature is within the ideal range: {current_temp}°F."

        # Feedback on wind comparison
        if not wind_match:
            if current_wind > ideal_wind + 5:
                wind_feedback = f"Wind speed too high! Current Wind: {current_wind} mph."
            else:
                wind_feedback = f"Wind speed too low! Current Wind: {current_wind} mph."
        else:
            wind_feedback = f"Wind speed is within the ideal range: {current_wind} mph."
        
        # Combine results
        result = f"{temp_feedback}\n{wind_feedback}"

        # Final message on whether conditions are ideal
        if temp_match and wind_match:
            result += "\nIdeal weather conditions met!"
        else:
            result += "\nIdeal weather conditions not met."
            # Update the label with the result
        self.ui.ideal_weather_label.setText(result)  # Display results in the new label