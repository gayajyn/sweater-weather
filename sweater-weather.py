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
    def __init__(self, num_clth, clth_data):
        super().__init__()
        self.setWindowTitle("Clothing Questionnaire")
        self.layout = QVBoxLayout()
        self.row_input = []
        for i in range(num_clth):
            row = QHBoxLayout()
            row.addWidget(QLabel("In "))
            # Season dropdown
            season = QComboBox()
            season.addItems(["All Seasons", "Spring", "Summer", "Autumn", "Winter"])
            row.addWidget(season)
            row.addWidget(QLabel(", you'll need "))
            # Clothing name text input
            clothing = QLineEdit()
            row.addWidget(clothing)
            row.addWidget(QLabel(" when the "))
            # Weather factor dropdown
            factor = QComboBox()
            factor.addItems(["Temperature (F)", "Precipitation (0 = None, 1 = Rain, 2 = Snow, 3 = Mixed)", "Wind Speed (mph)"])
            row.addWidget(factor)
            row.addWidget(QLabel(" is between "))
            # Minimum value picker
            min_value = QSpinBox()
            min_value.setMinimum(-80)
            min_value.setMaximum(140)
            row.addWidget(min_value)
            row.addWidget(QLabel(" and "))
            # Maximum value picker
            max_value = QSpinBox()
            max_value.setMinimum(-80)
            max_value.setMaximum(140)
            row.addWidget(max_value)
            row.addWidget(QLabel("."))
            # Autofill form fields if clothing.json exists
            if i < len(clth_data):
                season.setCurrentIndex(clth_data[i][0])
                clothing.setText(clth_data[i][1])
                factor.setCurrentIndex(clth_data[i][2])
                min_value.setValue(clth_data[i][3])
                max_value.setValue(clth_data[i][4])
            self.row_input.append([season, clothing, factor, min_value, max_value])  # Group input widgets
            self.layout.addLayout(row)
        self.buttons = QHBoxLayout()  # Menu row
        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save)
        self.buttons.addWidget(self.save_btn)
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.buttons.addWidget(self.cancel_btn)
        # Add buttons to row
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
                        # Prevent negative wind speeds
                        if min_value.value() < 0:
                            error_message("Wind speed values cannot be negative.")
                            return
                        factor = "wind speed"
                    elif factor_label.currentText() == "Precipitation (0 = None, 1 = Rain, 2 = Snow, 3 = Mixed)":
                        # Prevent out-of-range precipitation values
                        if min_value.value() < 0 or max_value.value() > 3:
                            error_message("Precipitation values must be between 0 and 3.")
                            return
                        factor = "precipitation"
                    else:
                        factor = "temperature"
                    responses.append({"season": season.currentText().lower(), "clothing": clothing.text(), "factor": factor, "min": min_value.value(), "max": max_value.value()})
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
            self.accept()
        except Exception as e:
            error_message(f"Error saving clothing preferences: {e}")


# Window to set rating preferences
class RatingQuestionnaire(QDialog):
    def __init__(self, num_ratg, ratg_data):
        super().__init__()
        self.setWindowTitle("Rating Questionnaire")
        self.layout = QVBoxLayout()
        self.row_input = []
        for i in range(num_ratg):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{i + 1}. The weather is "))
            # Rating text box
            rating = QLineEdit()
            row.addWidget(rating)
            row.addWidget(QLabel(" when the "))
            # Weather factor dropdown
            factor = QComboBox()
            factor.addItems(["Temperature (F)", "Precipitation (0 = None, 1 = Rain, 2 = Snow, 3 = Mixed)", "Wind Speed (mph)"])
            row.addWidget(factor)
            row.addWidget(QLabel(" is between "))
            # Minimum value picker
            min_value = QSpinBox()
            min_value.setMinimum(-80)
            min_value.setMaximum(140)
            row.addWidget(min_value)
            row.addWidget(QLabel(" and "))
            # Maximum value picker
            max_value = QSpinBox()
            max_value.setMinimum(-80)
            max_value.setMaximum(140)
            row.addWidget(max_value)
            row.addWidget(QLabel("."))
            # Autofill form fields if clothing.json exists
            if i < len(ratg_data):
                rating.setText(ratg_data[i][0])
                factor.setCurrentIndex(ratg_data[i][1])
                min_value.setValue(ratg_data[i][2])
                max_value.setValue(ratg_data[i][3])
            self.row_input.append([rating, factor, min_value, max_value])  # Group input widgets
            self.layout.addLayout(row)
        self.buttons = QHBoxLayout()  # Menu row
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

    # Save input into ratings.json
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
                        # Prevent negative wind speeds
                        if min_value.value() < 0:
                            error_message("Wind speed values cannot be negative.")
                            return
                        factor = "wind speed"
                    elif factor_label.currentText() == "Precipitation (0 = None, 1 = Rain, 2 = Snow, 3 = Mixed)":
                        # Prevent out-of-range precipitation values
                        if min_value.value() < 0 or max_value.value() > 3:
                            error_message("Precipitation values must be between 0 and 3.")
                            return
                        factor = "precipitation"
                    else:
                        factor = "temperature"
                    responses.append({"rating": rating.text(), "factor": factor, "min": min_value.value(), "max": max_value.value()})
                # If a text box is empty, send a confirmation message
                elif not ignore_blanks:
                    ok = QMessageBox.question(self, "Ignore Empty Fields", "Empty entries will be discarded, do you want to continue?", QMessageBox.Yes | QMessageBox.No)
                    if ok == QMessageBox.Yes:
                        ignore_blanks = True
                    else:
                        return
            # Store preferences into clothing.json
            with open("ratings.json", "w") as file:
                json.dump(responses, file)
            success_message("Rating preferences saved successfully.")
            self.accept()
        except Exception as e:
            error_message(f"Error saving preferences: {e}")


# Main application
class SweaterWeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sweater Weather")
        self.setGeometry(500, 200, 0, 0)
        self.current_season = self.get_season()
        self.initUI()

    def get_season(self):
        month = datetime.now().month
        if 3 <= month <= 5:
            return "spring"
        elif 6 <= month <= 8:
            return "summer"
        elif 9 <= month <= 11:
            return "autumn"
        else:
            return "winter"

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
        if self.current_season == "spring":
            gradient = QLinearGradient(0, 0, 1, 1)
            gradient.setColorAt(0, QColor("#A7D3A6"))
            gradient.setColorAt(1, QColor("#FFC0CB"))
        elif self.current_season == "summer":
            gradient = QLinearGradient(0, 0, 1, 1)
            gradient.setColorAt(0, QColor("#FFD700"))
            gradient.setColorAt(1, QColor("#87CEEB"))
        elif self.current_season == "autumn":
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
        season_label = QLabel(f"Theme: {self.current_season.title()}")
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
        self.forecast_display = QLabel()  # Forecast report
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
        row1 = QHBoxLayout()  # Options row
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
        row2 = QHBoxLayout()  # Options row
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
        try:
            # Fetch existing preferences if available
            with open("clothing.json", "r") as file:
                prefs = json.load(file)
            # Convert to autofill data
            clth_data = []
            for p in prefs:
                clth_data.append([["all seasons", "spring", "summer", "autumn", "winter"].index(p["season"]), p["clothing"], ["temperature", "precipitation", "wind speed"].index(p["factor"]), p["min"], p["max"]])
            ClothingQuestionnaire(self.num_clth.value(), clth_data).exec_()  # Open autofilled questionnaire
        except Exception:
            ClothingQuestionnaire(self.num_clth.value(), []).exec_()  # Open blank questionnaire
        self.clth_display.setText(self.display_clothing())  # Update display aftrer submission

    # Opens rating questionnaire
    def edit_ratings(self):
        try:
            # Fetch existing preferences if available
            with open("ratings.json", "r") as file:
                prefs = json.load(file)
            ratg_data = []
            for p in prefs:
                ratg_data.append([p["rating"], ["temperature", "precipitation", "wind speed"].index(p["factor"]), p["min"], p["max"]])
            RatingQuestionnaire(self.num_ratg.value(), ratg_data).exec_()  # Open autofilled questionnaire
        except Exception:
            RatingQuestionnaire(self.num_ratg.value(), []).exec_()  # Open blank questionnaire
        self.ratg_display.setText(self.display_ratings())  # Update display after submission

    # Gets and prints saved preferences from clothing.json
    def display_clothing(self):
        try:
            with open("clothing.json", "r") as file:
                prefs = json.load(file)
            text = ""
            for p in prefs:
                if p["season"] == "all seasons":
                    season = ""
                else:
                    season = p["season"] + " "
                if p["min"] == p["max"]:
                    min_max = str(p["min"])
                else:
                    min_max = str(p["min"]) + " - " + str(p["max"])
                text += "{}: {}{} is {}\n".format(p["clothing"], season, p["factor"], min_max)  # Row formatting
            return text
        except FileNotFoundError:
            return "No saved clothing preferences."
        except Exception as e:
            return f"Unable to load clothing preferences.\nError details: {e}"

    # Gets and prints saved preferences from ratings.json
    def display_ratings(self):
        try:
            with open("ratings.json", "r") as file:
                prefs = json.load(file)
            text = ""
            for p in prefs:
                if p["min"] == p["max"]:
                    min_max = str(p["min"])
                else:
                    min_max = str(p["min"]) + " - " + str(p["max"])
                text += "{}: {} is {}\n".format(p["rating"], p["factor"], min_max)  # Row formatting
            return text
        except FileNotFoundError:
            return "No saved rating preferences."
        except Exception as e:
            return f"Unable to load rating preferences\nError details: {e}"

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
            self.forecast_label.setText(f"Error fetching weather data. Try selecting a different location, or try again later.\nError details: {e}")

    # Gets current location using IP address
    def fetch_current_location(self):
        try:
            response = requests.get("http://ip-api.com/json/")
            if response.status_code == 200:
                data = response.json()
                return data['lat'], data['lon'], data['city'], data['regionName']
        except Exception as e:
            self.status.setText(f"Error fetching location data. Try selecting a different location, or try again later.\nError details: {e}")

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
                self.status.setText(f"Fetching forecast for {city}, {region}...")
            # Text input method - prevent empty or invalid input
            elif city_name:
                geocoder = Nominatim(user_agent="sweater-weather")
                location = geocoder.geocode(city_name)
                if location:
                    lat, lon = location.latitude, location.longitude
                    self.status.setText(f"Fetching forecast for {city_name}...")
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
                    self.status.setText("No forecast data available. Try selecting a differernt locaiton.")
            else:
                self.status.setText("Could not determine location. Try selecting a different location.")
        except Exception as e:
            self.status.setText(f"Error fetching forecast data. Try selecting a different location.\nError details: {e}")

    # Determines which user preferences are met by forecast data
    def report(self, periods):
        try:
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
            header = "No suggestions for the coming week."  # Report when no suggestions are given
            report = ""
            for p in periods:
                time, temp, precip_fc, wind_fc = p["name"], int(p["temperature"]), p["detailedForecast"], p["windSpeed"]  # Get forecast value for each weather factor
                # Determine precipitation based on keywords from the detailed forecast
                if any(i in precip_fc.lower() for i in ["mixed", "mix", "sleet", "hail", "ice", "slush", "freezing rain", "frozen rain"]):
                    precip = "Mixed"
                elif any(i in precip_fc.lower() for i in ["snow", "snowfall", "blizzard", "flurry", "flurries", "flurrying"]):
                    if any(i in precip_fc.lower() for i in ["rain", "rainfall", "thunderstorm", "thunderstorms"]):  # Both rain and snow mentioned is Mixed
                        precip = "Mixed"
                    else:
                        precip = "Snow"
                elif any(i in precip_fc.lower() for i in ["rain", "rainfall", "shower", "showers", "thunderstorm", "thunderstorms"]):
                    precip = "Rain"
                else:
                    precip = "None"
                wind = max(int(i) for i in re.findall(r'\d+', wind_fc))  # Extract max wind speed from forecasted range
                suggestions = []
                for r in ratings:
                    # Apply rating if it meets the criteria
                    if r["factor"] == "temperature" and r["min"] <= temp <= r["max"]:
                        suggestions.append(r["rating"])
                        break
                    elif r["factor"] == "precipitation" and r["min"] <= ["None", "Rain", "Snow", "Mixed"].index(precip) <= r["max"]:
                        suggestions.append(r["rating"])
                        break
                    elif r["factor"] == "wind speed" and r["min"] <= wind <= r["max"]:
                        suggestions.append(r["rating"])
                        break
                for c in clothing:
                    # Add clothing items if it meets the criteria
                    if (c["season"] == "all seasons" or c["season"] == self.current_season) and not any([c["clothing"] == i for i in suggestions]):
                        if c["factor"] == "temperature" and c["min"] <= temp <= c["max"]:
                            suggestions.append(c["clothing"])
                        elif c["factor"] == "precipitation" and c["min"] <= ["None", "Rain", "Snow", "Mixed"].index(precip) <= c["max"]:
                            suggestions.append(c["clothing"])
                        elif c["factor"] == "wind speed" and c["min"] <= wind <= c["max"]:
                            suggestions.append(c["clothing"])
                if suggestions:
                    report += "{0:<25}\t{1:<15}\t{2:<15}\t{3:<15}\t".format(time, temp, precip, wind) + ", ".join(suggestions) + "\n"
            if report:
                header = "{0:<25}\t{1:<15}\t{2:<15}\t{3:<15}\t{4:<15}\t".format("Time", "Temp (F)", "Precipitation", "Wind (mph)", "Suggestions")
            return header, report
        except Exception as e:
            return f"Unable to generate report.\nError details: {e}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = SweaterWeatherApp()
    main_window.show()
    sys.exit(app.exec_())
