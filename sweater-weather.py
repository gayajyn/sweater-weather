import json
import re
import requests
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QLineEdit, QCheckBox, QTabWidget, QMessageBox, QDialog, QSpinBox,
    QComboBox, QHBoxLayout
)
from PyQt5.QtGui import QPalette, QLinearGradient, QColor, QBrush
from PyQt5.QtCore import Qt
from datetime import datetime
from geopy.geocoders import Nominatim


# Opens a new dialog showing an error message
def error_message(message):
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Error")
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


# Opens a new dialog showing a task success message
def success_message(message):
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Success")
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


# Window to set clothing preferences
class ClothingQuestionnaire(QDialog):
    def __init__(self, num_clth):
        super().__init__()
        self.setWindowTitle("Clothing Questionnaire")
        self.layout = QVBoxLayout()
        # Generate rows for input
        self.responses = []
        self.row_input = []
        for i in range(num_clth):
            row = QHBoxLayout()
            row.addWidget(QLabel("In "))
            # Season dropdown
            season = QComboBox()
            season.addItems(["Spring", "Summer", "Autumn", "Winter"])
            row.addWidget(season)
            row.addWidget(QLabel(", you need "))
            # Clothing name text input
            clothing = QLineEdit()
            row.addWidget(clothing)
            row.addWidget(QLabel(" when the "))
            # Weather factor dropdown
            factor = QComboBox()
            factor.addItems(["Temperature (F)", "Precipitation (0 = No, 1 = Yes)", "Wind Speed (mph)"])
            row.addWidget(factor)
            row.addWidget(QLabel(" is between "))
            # Minimum value picker
            min_value = QSpinBox()
            min_value.setMinimum(-75)
            min_value.setMaximum(175)
            row.addWidget(min_value)
            row.addWidget(QLabel(" and "))
            # Maximum value picker
            max_value = QSpinBox()
            max_value.setMinimum(-75)
            max_value.setMaximum(175)
            row.addWidget(max_value)
            row.addWidget(QLabel("."))
            # Get input widgets for row
            self.row_input.append([season, clothing, factor, min_value, max_value])
            self.layout.addLayout(row)
        # Row for buttons
        self.buttons = QHBoxLayout()
        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save)
        self.buttons.addWidget(self.save_btn)
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.buttons.addWidget(self.cancel_btn)
        self.layout.addLayout(self.buttons)
        self.setLayout(self.layout)

    # Save input into clothing.json
    def save(self):
        responses = []
        ignore_blanks = False
        try:
            for season, clothing, factor_label, min_value, max_value in self.row_input:
                if clothing.text().strip():
                    # Prevent incorrect range
                    if min_value.value() > max_value.value():
                        error_message("Minimum value cannot be larger than the maximum value.")
                        return
                    # Rename weather factor
                    if factor_label.currentText() == "Wind Speed (mph)":
                        factor = "wind_speed"
                    elif factor_label.currentText() == "Precipitation (0 = No, 1 = Yes)":
                        factor = "precipitation"
                    else:
                        factor = "temperature"
                    # Add dictionary item
                    responses.append({"season": season.currentText(), "clothing": clothing.text(), "factor": factor, "min": min_value.value(), "max": max_value.value()})
                # If a text box is empty, send a confirmation message
                elif not ignore_blanks:
                    ok = QMessageBox.question(self, "Ignore Empty Fields", "There are empty fields. These will be discarded, do you want to continue?", QMessageBox.Yes | QMessageBox.No)
                    if ok == QMessageBox.Yes:
                        ignore_blanks = True
                    else:
                        return
            # Store preferences into clothing.json
            with open("clothing.json", "w") as file:
                json.dump(responses, file)
            success_message("Clothing preferences saved successfully.")
            # Close window
            self.accept()
        except Exception as e:
            error_message(f"Error saving clothing preferences: {e}")


# Window to set rating preferences
class RatingQuestionnaire(QDialog):
    def __init__(self, num_ratg):
        super().__init__()
        self.setWindowTitle("Rating Questionnaire")
        self.layout = QVBoxLayout()
        # Generate rows for input
        self.responses = []
        self.row_input = []
        for i in range(num_ratg):
            row = QHBoxLayout()
            row.addWidget(QLabel("The weather is "))
            # Rating text box
            rating = QLineEdit()
            row.addWidget(rating)
            row.addWidget(QLabel(" when the "))
            # Weather factor dropdown
            factor = QComboBox()
            factor.addItems(["Temperature", "Precipitation (0 = No, 1 = Yes)", "Wind Speed (mph)"])
            row.addWidget(factor)
            row.addWidget(QLabel(" is between "))
            # Minimum value picker
            min_value = QSpinBox()
            min_value.setMinimum(-75)
            min_value.setMaximum(175)
            row.addWidget(min_value)
            row.addWidget(QLabel(" and "))
            # Maximum value picker
            max_value = QSpinBox()
            max_value.setMinimum(-75)
            max_value.setMaximum(175)
            row.addWidget(max_value)
            row.addWidget(QLabel("."))
            # Get input widgets for row
            self.row_input.append([rating, factor, min_value, max_value])
            self.layout.addLayout(row)
        # Row for buttons
        self.buttons = QHBoxLayout()
        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save)
        self.buttons.addWidget(self.save_btn)
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.buttons.addWidget(self.cancel_btn)
        self.layout.addLayout(self.buttons)
        self.setLayout(self.layout)

    # Save input into clothing.json
    def save(self):
        responses = []
        ignore_blanks = False
        try:
            for rating, factor_label, min_value, max_value in self.row_input:
                if rating.text().strip():
                    # Prevent incorrect range
                    if min_value.value() > max_value.value():
                        error_message("Minimum value cannot be larger than the maximum value.")
                        return
                    # Rename weather factor
                    if factor_label.currentText() == "Wind Speed (mph)":
                        factor = "wind_speed"
                    elif factor_label.currentText() == "Precipitation (0 = No, 1 = Yes)":
                        factor = "precipitation"
                    else:
                        factor = "temperature"
                    # Add dictionary item
                    responses.append({"rating": rating.text(), "factor": factor, "min": min_value.value(), "max": max_value.value()})
                # If a text box is empty, send a confirmation message
                elif not ignore_blanks:
                    ok = QMessageBox.question(self, "Ignore Empty Fields", "There are empty fields. These will be discarded, do you want to continue?", QMessageBox.Yes | QMessageBox.No)
                    if ok == QMessageBox.Yes:
                        ignore_blanks = True
                    else:
                        return
            # Store preferences into clothing.json
            with open("ratings.json", "w") as file:
                json.dump(responses, file)
            success_message("Rating preferences saved successfully.")
            # close window
            self.accept()
        except Exception as e:
            error_message(f"Error saving preferences: {e}")


# Main application
class SweaterWeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sweater Weather")
        self.setGeometry(500, 200, 500, 250)
        self.current_season = self.get_season()
        self.initUI()

    def get_season(self):
        month = datetime.now().month
        if 3 <= month <= 5:
            return "Spring"
        elif 6 <= month <= 8:
            return "Summer"
        elif 9 <= month <= 11:
            return "Autumn"
        else:
            return "Winter"

    def initUI(self):
        self.tabs = QTabWidget()
        self.apply_seasonal_theme()
        # Home tab
        self.home_tab = self.create_home_tab()
        self.tabs.addTab(self.home_tab, "Home")
        # Settings tab
        self.settings_tab = self.create_settings_tab()
        self.tabs.addTab(self.settings_tab, "Settings")
        self.setCentralWidget(self.tabs)

    # Changes color of UI based on the current season
    def apply_seasonal_theme(self):
        palette = QPalette()
        if self.current_season == "Spring":
            gradient = QLinearGradient(0, 0, 1, 1)
            gradient.setColorAt(0, QColor("#A7D3A6"))
            gradient.setColorAt(1, QColor("#FFC0CB"))
        elif self.current_season == "Summer":
            gradient = QLinearGradient(0, 0, 1, 1)
            gradient.setColorAt(0, QColor("#FFD700"))
            gradient.setColorAt(1, QColor("#87CEEB"))
        elif self.current_season == "Autumn":
            gradient = QLinearGradient(0, 0, 1, 1)
            gradient.setColorAt(0, QColor("#FF7F50"))
            gradient.setColorAt(1, QColor("#8B4513"))
        else:
            gradient = QLinearGradient(0, 0, 1, 1)
            gradient.setColorAt(0, QColor("#B0E0E6"))
            gradient.setColorAt(1, QColor("#FFFFFF"))

        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

    # Home tab UI
    def create_home_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        # Welcome message
        welcome_label = QLabel("<b>Welcome to Sweater Weather!</b>")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        # Display season
        season_label = QLabel(f"Theme: {self.current_season}")
        season_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(season_label)
        # Location name input
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter City Name (e.g., Richardson, TX)")
        layout.addWidget(self.location_input)
        # Use Current Location checkbox
        self.use_current_location = QCheckBox("Use My Current Location")
        self.use_current_location.stateChanged.connect(self.toggle_location_input)
        layout.addWidget(self.use_current_location)
        # Fetch Forecast button
        fetch_btn = QPushButton("Get Forecast")
        fetch_btn.clicked.connect(self.handle_forecast_fetch)
        layout.addWidget(fetch_btn)
        # Status/report header
        self.status = QLabel("Weather forecast will appear here.")
        layout.addWidget(self.status)
        # Forecast report
        self.forecast_display = QLabel()
        self.forecast_display.setWordWrap(True)  # Enable text wrapping
        layout.addWidget(self.forecast_display)
        tab.setLayout(layout)
        return tab

    # Settings tab UI
    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        # Clothing preferences display
        layout.addWidget(QLabel("<b>Saved Clothing Preferences:</b>"))
        self.clth_display = QLabel(self.display_clothing())
        layout.addWidget(self.clth_display)
        # Options row
        row1 = QHBoxLayout()
        # Choose number of rows
        row1.addWidget(QLabel("Number of preferences (1 - 20):"), alignment=Qt.AlignRight)
        self.num_clth = QSpinBox()
        self.num_clth.setFixedWidth(50)
        self.num_clth.setMinimum(1)
        self.num_clth.setMaximum(20)
        row1.addWidget(self.num_clth, alignment=Qt.AlignLeft)
        # Clothing questionnaire button
        self.clth_btn = QPushButton("Change Clothing Preferences")
        self.clth_btn.setFixedWidth(300)
        self.clth_btn.clicked.connect(self.edit_clothing)
        row1.addWidget(self.clth_btn)
        layout.addLayout(row1)
        # Rating preferences display
        layout.addWidget(QLabel("<b>Saved Rating Preferences:</b>"))
        self.ratg_display = QLabel(self.display_ratings())
        layout.addWidget(self.ratg_display)
        # Options row
        row2 = QHBoxLayout()
        # Choose number of rows
        row2.addWidget(QLabel("Number of preferences (1 - 20):"))
        self.num_ratg = QSpinBox()
        self.num_ratg.setFixedWidth(50)
        self.num_ratg.setMinimum(1)
        self.num_ratg.setMaximum(20)
        row2.addWidget(self.num_ratg, alignment=Qt.AlignLeft)
        # Rating questionnaire button
        self.ratg_btn = QPushButton("Change Rating Preferences")
        self.ratg_btn.setFixedWidth(300)
        self.ratg_btn.clicked.connect(self.edit_ratings)
        row2.addWidget(self.ratg_btn)
        layout.addLayout(row2)
        tab.setLayout(layout)
        return tab

    # Opens clothing questionnaire
    def edit_clothing(self):
        ClothingQuestionnaire(self.num_clth.value()).exec_()
        self.clth_display.setText(self.display_clothing())

    # Opens rating questionnaire
    def edit_ratings(self):
        RatingQuestionnaire(self.num_ratg.value()).exec_()
        self.ratg_display.setText(self.display_ratings())

    # Gets and prints saved preferences from clothing.json
    def display_clothing(self):
        text = ""
        try:
            with open("clothing.json", "r") as file:
                prefs = json.load(file)
            for p in prefs:
                # Row formatting
                text += "\n{} ({}): {}   {} - {}".format(p["clothing"], p["season"], p["factor"], str(p["min"]), str(p["max"]))
            return text
        except FileNotFoundError:
            return "No saved clothing preferences."
        except Exception as e:
            return f"Unable to load clothing preferences : {e}"

    # Gets and prints saved preferences from ratings.json
    def display_ratings(self):
        text = ""
        try:
            with open("ratings.json", "r") as file:
                prefs = json.load(file)
            for p in prefs:
                # Row formatting
                text += "\n{}: {}   {} - {}".format(p["rating"], p["factor"], str(p["min"]), str(p["max"]))
            return text
        except FileNotFoundError:
            return "No saved rating preferences."
        except Exception as e:
            return f"Unable to load rating preferences: {e}"

    # Gets weather data from NWS API as JSON
    def fetch_weather_data(self, lat, lon):
        try:
            response = requests.get(f"https://api.weather.gov/points/{lat},{lon}")
            if response.status_code == 200:
                forecast_url = response.json()['properties']['forecast']
                forecast_response = requests.get(forecast_url)
                if forecast_response.status_code == 200:
                    return forecast_response.json()
        except Exception as e:
            self.forecast_label.setText(f"Error fetching weather data: {e}")

    # Gets current location using IP address
    def fetch_current_location(self):
        try:
            response = requests.get("http://ip-api.com/json/")
            if response.status_code == 200:
                data = response.json()
                return data['lat'], data['lon'], data['city'], data['regionName']
        except Exception as e:
            self.status.setText(f"Error fetching location data: {e}")

    # Disables location text input when Get Current Locaiton is checked
    def toggle_location_input(self, state):
        self.location_input.setDisabled(state == Qt.Checked)

    # Gets forecast data
    def handle_forecast_fetch(self):
        try:
            # Get coordinates
            city_name = self.location_input.text()
            # IP method
            if self.use_current_location.isChecked():
                location_data = self.fetch_current_location()
                lat, lon, city, region = location_data
                self.status.setText(f"Fetching forecast for your location: {city}, {region}")
            # Text input method - prevent empty or invalid input
            elif city_name:
                geocoder = Nominatim(user_agent="sweater-weather")
                location = geocoder.geocode(city_name)
                if location:
                    lat, lon = location.latitude, location.longitude
                    self.status.setText(f"Fetching forecast for: {city_name}")
                else:
                    self.status.setText("Invalid city name, please try again.")
                    return
            else:
                self.status.setText("Please enter a city or enable 'Use My Current Location'.")
                return
            # Fetch and display weather data
            if lat and lon:
                weather_data = self.fetch_weather_data(lat, lon)
                if weather_data:
                    periods = weather_data['properties']['periods']
                    # Generate report
                    header, report = self.report(periods)
                    self.status.setText(header)
                    self.forecast_display.setText(report)
                else:
                    self.status.setText("No forecast data available.")
            else:
                self.status.setText("Could not determine location.")
        except Exception as e:
            self.status.setText(f"Error fetching forecast data: {e}")

    # Determines which user preferences are met by forecast data
    def report(self, periods):
        try:
            # Read clothing.json and rating.json
            try:
                with open("clothing.json", "r") as file:
                    clothing = json.load(file)
            except FileNotFoundError:
                clothing = []
            try:
                with open("ratings.json", "r") as file:
                    ratings = json.load(file)
            except FileNotFoundError:
                ratings = []
            if not clothing and not ratings:
                return "No saved preferences. Set up preferences in the Settings tab.", None
            # Default header, modified if there are suggestions
            header = "No suggestions for the coming week."
            report = ""
            for p in periods:
                # Get forecast value for each weather factor
                time, temp, precip_fc, wind_fc = p["name"], int(p["temperature"]), p["detailedForecast"], p["windSpeed"]
                # Determine precipitation based on keywords from the detailed forecast
                precip = any(i in precip_fc.lower() for i in ["rain", "shower", "showers", "thunderstorm", "thunderstorms", "snow", "blizzard", "ice", "sleet", "hail", "mix", "mixed"])
                # Determine max wind speed from the given range using regex
                wind = max(int(i) for i in re.findall(r'\d+', wind_fc))
                suggestions = []
                for c in clothing:
                    # Add clothing suggestion if it meets the criteria
                    if c["season"] == self.current_season:
                        if c["factor"] == "temperature" and temp >= c["min"] and temp <= c["max"] and c["clothing"] not in suggestions:
                            suggestions.append(c["clothing"])
                        if c["factor"] == "precipitation" and ((precip and c["max"] >= 1) or (not precip and c["max"] <= 0)) and c["clothing"] not in suggestions:
                            suggestions.append(c["clothing"])
                        if c["factor"] == "wind_speed" and wind >= c["min"] and wind <= c["max"] and c["clothing"] not in suggestions:
                            suggestions.append(c["clothing"])
                for r in ratings:
                    # Add rating suggestion if it meets the criteria
                    if r["factor"] == "temperature" and temp >= r["min"] and temp <= r["max"] and r["rating"] not in suggestions:
                        suggestions.append(r["rating"])
                    if r["factor"] == "precipitation" and ((precip and r["max"] >= 1) or (not precip and r["max"] <= 0)) and r["rating"] not in suggestions:
                        suggestions.append(r["rating"])
                    if r["factor"] == "wind_speed" and wind >= r["min"] and wind <= r["max"] and r["rating"] not in suggestions:
                        suggestions.append(r["rating"])
                if suggestions:
                    # New header
                    header = "{0:<15}\t{1:<15}\t{2:<15}\t{3:<15}\t{4:<15}\t".format("Time", "Temperature (F)", "Precipitation", "Wind Speed (mph)", "Suggestions")
                    # Print row
                    if precip:
                        report += "{0:<15}\t{1:<15}\t{2:<15}\t{3:<15}\t".format(time, temp, "Yes", wind) + ", ".join(suggestions) + "\n"
                    else:
                        report += "{0:<15}\t{1:<15}\t{2:<15}\t{3:<15}\t".format(time, temp, "No", wind) + ", ".join(suggestions) + "\n"
            return header, report
        except Exception as e:
            return f"Unable to generate report: {e}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = SweaterWeatherApp()
    main_window.show()
    sys.exit(app.exec_())
