import sys
import json
import requests
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QTabWidget, 
    QWidget, QLineEdit, QCheckBox, QSpinBox, QDialog, QMessageBox, QHBoxLayout, QComboBox, QInputDialog
)
from PyQt5.QtGui import QPalette, QBrush, QLinearGradient, QColor
from PyQt5.QtCore import Qt


# Function to fetch weather data from NWS API
def fetch_weather_data(lat, lon):
    try:
        base_url = f"https://api.weather.gov/points/{lat},{lon}"
        response = requests.get(base_url)
        if response.status_code == 200:
            forecast_url = response.json()['properties']['forecast']
            forecast_response = requests.get(forecast_url)
            if forecast_response.status_code == 200:
                return forecast_response.json()
        return None
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None


# Function to fetch current location using IP address
def get_current_location():
    try:
        response = requests.get("http://ip-api.com/json/")
        if response.status_code == 200:
            data = response.json()
            return data['lat'], data['lon'], data['city'], data['regionName']
        else:
            print("Error: Unable to fetch location.")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


# Clothing Preferences Questionnaire Dialog
class AddClothing(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Preference")
        self.setGeometry(300, 300, 400, 300)
        self.layout = QVBoxLayout()
        self.name_label = QLabel("Clothing Name:")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.weather_label = QLabel("Weather Type:")
        self.weather_dropdown = QComboBox()
        self.weather_dropdown.addItems(["Temperature", "Precipitation", "Wind Speed"])
        self.layout.addWidget(self.weather_label)
        self.layout.addWidget(self.weather_dropdown)
        self.min_label = QLabel("Minimum Value:")
        self.min_input = QSpinBox()
        self.layout.addWidget(self.min_label)
        self.layout.addWidget(self.min_input)
        self.max_label = QLabel("Maximum Value:")
        self.max_input = QSpinBox()
        self.layout.addWidget(self.max_label)
        self.layout.addWidget(self.max_input)
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_clothing)
        self.layout.addWidget(self.add_button)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        self.layout.addWidget(self.cancel_button)
        self.setLayout(self.layout)
        

    def add_clothing(self):
        name = self.name_input.text().strip()
        weather_type = self.weather_dropdown.currentText()
        min_value = self.min_input.value()
        max_value = self.max_input.value()
        if not name:
            QMessageBox.warning(self, "Error", "Clothing name cannot be empty.")
            return
        if max_value < min_value:
            QMessageBox.warning(self, "Error", "Maximum value cannot be less than the minimum value.")
            return
        self.new_clothing = {
            "weather_type": weather_type,
            "min": min_value,
            "max": max_value
        }
        try:
            with open("clothing_preferences.json", "w") as file:
                json.dump(self.new_clothing, file)  
            QMessageBox.information(self, "Success", f"Added clothing: {name}")
            self.close()
        except:
            self.show_error_message("There was an error while tryiing to add the clothing item.")


# Main Application Class
class SweaterWeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sweater Weather")
        self.setGeometry(100, 100, 800, 600)
        self.clothing_preferences = {}
        self.temperature_preferences = {"min_temp": 60, "max_temp": 80}       
        self.check_and_load_preferences()
        self.current_season = self.get_season()
        self.initUI()
    
    def open_add_clothing(self):
       self.add_window = AddClothing()
       self.add_window.show()
       self.add_window.add_button.clicked.connect(self.update_clothing)

    def update_clothing(self):
        self.clothing.update(self.add_window.clothing)
        self.update_display()

    def remove_clothing(self):
        items = list(self.clothing.keys())
        if not items:
            QMessageBox.warning(self, "Error", "No clothing items have been added.")
            return
        rank, ok = QInputDialog.getInt(self, "Remove Clothing", "Enter the rank of the item to remove :", 1, 1, len(items))
        if ok:
            del self.clothing[items[rank - 1]]
            self.update_clothing_display()
    
    def update_clothing_display(self):
        display_text = "\n".join([f"{rank + 1}. {name}: {props}" for rank, (name, props) in enumerate(self.clothing.items())])
        self.display_label.setText(f"Clothing Items:\n{display_text}")

    def check_and_load_preferences(self):
        try:
            with open("clothing_preferences.json", "r") as file:
                self.clothing_preferences = json.load(file)
        except:
            self.save_clothing_preferences()
        try:
            with open("temperature_preferences.json", "r") as file:
                self.temperature_preferences = json.load(file)
        except FileNotFoundError:
            self.save_temperature_preferences()

    def save_temperature_preferences(self):
        with open("temperature_preferences.json", "w") as file:
            json.dump(self.temperature_preferences, file)
            
    def save_clothing_preferences(self):
        with open("clothing_preferences.json", "w") as file:
            json.dump(self.clothing_preferences, file)

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
        self.home_tab = self.create_home_tab()
        self.tabs.addTab(self.home_tab, "Home")
        self.preferences_tab = self.create_preference_settings_tab()
        self.tabs.addTab(self.preferences_tab, "Preferences")
        self.clothing_tab = self.create_clothing_settings_tab()
        self.tabs.addTab(self.clothing_tab, "Clothing")

        self.setCentralWidget(self.tabs)

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

    def create_home_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Welcome Message
        welcome_label = QLabel(f"Welcome to Sweater Weather! ({self.current_season})")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        # Location Input Field
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter City Name (e.g., Richardson, TX)")
        layout.addWidget(self.location_input)

        # Use Current Location Checkbox
        self.use_current_location = QCheckBox("Use My Current Location")
        self.use_current_location.stateChanged.connect(self.toggle_location_input)
        layout.addWidget(self.use_current_location)

        # Fetch Forecast Button
        fetch_btn = QPushButton("Get Forecast")
        fetch_btn.clicked.connect(self.handle_forecast_fetch)
        layout.addWidget(fetch_btn)

        # Forecast Display
        self.forecast_label = QLabel("Weather forecast will appear here.")
        self.forecast_label.setWordWrap(True)  # Enable text wrapping
        layout.addWidget(self.forecast_label)

        tab.setLayout(layout)
        return tab
    
    def create_clothing_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>Customize Your Clothing Preferences</b>"))
        layout.addWidget(QLabel("Clothing Items:"))
        add_button = QPushButton("Add Clothing")
        add_button.clicked.connect(self.open_add_clothing)
        layout.addWidget(add_button)
        remove_button = QPushButton("Remove Clothing")
        remove_button.clicked.connect(self.remove_clothing)
        layout.addWidget(remove_button)
        tab.setLayout(layout)
        return tab

    def create_preference_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("<b>Customize Your Weather Preferences</b>"))
        layout.addWidget(QLabel("Set your ideal temperature range (°F):"))

        min_temp_layout = QHBoxLayout()
        min_temp_label = QLabel("Minimum Temperature:")
        self.min_temp_spinbox = QSpinBox()
        self.min_temp_spinbox.setRange(-50, 120)
        self.min_temp_spinbox.setValue(self.temperature_preferences["min_temp"])
        self.min_temp_spinbox.setSuffix(" °F")
        min_temp_layout.addWidget(min_temp_label)
        min_temp_layout.addWidget(self.min_temp_spinbox)
        layout.addLayout(min_temp_layout)

        max_temp_layout = QHBoxLayout()
        max_temp_label = QLabel("Maximum Temperature:")
        self.max_temp_spinbox = QSpinBox()
        self.max_temp_spinbox.setRange(-50, 120)
        self.max_temp_spinbox.setValue(self.temperature_preferences["max_temp"])
        self.max_temp_spinbox.setSuffix(" °F")
        max_temp_layout.addWidget(max_temp_label)
        max_temp_layout.addWidget(self.max_temp_spinbox)
        layout.addLayout(max_temp_layout)

        save_btn = QPushButton("Save Preferences")
        save_btn.clicked.connect(self.save_preferences)
        layout.addWidget(save_btn)

        tab.setLayout(layout)
        return tab

    def toggle_location_input(self, state):
        self.location_input.setDisabled(state == Qt.Checked)

    def handle_forecast_fetch(self):
        # Determine location
        if self.use_current_location.isChecked():
            location_data = get_current_location()
            if location_data:
                lat, lon, city, region = location_data
                self.forecast_label.setText(f"Fetching forecast for your location: {city}, {region}")
            else:
                self.forecast_label.setText("Unable to determine your current location.")
                return
        else:
            city_name = self.location_input.text()
            if city_name:
                lat, lon = 32.9482, -96.7299  # Replace with geocoding logic
                self.forecast_label.setText(f"Fetching forecast for: {city_name}")
            else:
                self.forecast_label.setText("Please enter a city or enable 'Use My Current Location'.")
                return

        # Fetch and display weather data
        weather_data = fetch_weather_data(lat, lon)
        if weather_data:
            periods = weather_data['properties']['periods']
            if periods:
                self.suggest_clothing(periods)
            else:
                self.forecast_label.setText("No forecast data available.")
        else:
            self.forecast_label.setText("Error fetching forecast. Please try again.")

    def suggest_clothing(self, periods):
        clothing_suggestions = []
        last_suggestion = None

        for period in periods:
            temp = period['temperature']
            time = period['name']
            season = self.current_season

            # Determine the clothing suggestion based on temperature
            suggestion = None  # No default text
            if season in self.clothing_preferences:
                if season == "Summer" and temp >= 85:
                    suggestion = self.clothing_preferences["Summer"]
                elif season == "Spring" and 60 <= temp <= 70:
                    suggestion = self.clothing_preferences["Spring"]
                elif season == "Autumn" and 50 <= temp <= 60:
                    suggestion = self.clothing_preferences["Autumn"]
                elif season == "Winter" and temp < 40:
                    suggestion = self.clothing_preferences["Winter"]

            # Only add a suggestion if one exists
            if suggestion:
                # Add transition notification if clothing recommendation changes
                if last_suggestion and last_suggestion != suggestion:
                    clothing_suggestions.append(f"Transition Alert: Consider changing to {suggestion} later.")

                # Append the suggestion for the current period
                clothing_suggestions.append(f"{time}: {temp}°F - {suggestion}")
                last_suggestion = suggestion

        # Display all suggestions or notify if no data is available
        suggestions_text = "\n".join(clothing_suggestions) if clothing_suggestions else "No significant clothing changes needed today."
        self.forecast_label.setText(suggestions_text)

    def save_preferences(self):
        min_temp = self.min_temp_spinbox.value()
        max_temp = self.max_temp_spinbox.value()

        if min_temp >= max_temp:
            self.show_error_message("Minimum temperature must be less than maximum temperature.")
            return

        self.temperature_preferences = {"min_temp": min_temp, "max_temp": max_temp}
        self.save_temperature_preferences()
        self.show_confirmation_dialog("Temperature preferences saved successfully!")

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_confirmation_dialog(self, message, title="Success"):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = SweaterWeatherApp()
    main_window.show()
    sys.exit(app.exec_())
