# Sweater Weather

Sweater Weather is a Python application that provides weather forecasts and personalized clothing suggestions based on current or forecasted temperatures. Users can set their preferred clothing for different seasons and ideal temperature ranges. The application can determine the user's location via IP address or accept manual city input.

Data sources: [NWS](https://www.weather.gov/documentation/services-web-api), [IP-API](https://ip-api.com/), [Nominatim](https://nominatim.org/)

Last update: 12/10/24

## Requirements

### PyQt5

```bash
conda install anaconda::pyqt
```

### Geopy
```bash
conda install conda-forge::geopy
```
## Instructions

### Running the application

```bash
python sweater-weather.py
```

### Home Tab
* If preferences are already set, usage can start here.
* Enter a city name or check "Use My Current Location" for automatic location detection.
* Click "Get Forecast" to get a text report of the weather forecast and its associated rating and clothing suggestions.
    * Only forecast periods with an associated rating or clothing item will appear.
    * The window may need to be stretched horizontally to achieve proper formatting.

### Settings Tab
* For first-time use, open the Settings tab, set the number of preferences you want to add, and click on "Edit Clothing". A new window will appear where you can enter and save your preferences.
* Select from the dropdowns and enter the name of the clothing item in the text box.
    * Example clothing items: sweater, jacket, umbrella
    * For precipitation, a maximum of 0 or below indicates that there is no precipitation forecasted, and 1 or greater indicates that there will be precipitation. This is determined by searching for keywords in the NWS detailed forecast.
* Once you click "Save", the preferences are saved in clothing.json, which will be in the same folder as sweater-weather.py. The program will lose access to the file if it is moved outside of the folder.
* Do the same for ratings. Note that the preferences are checked in order, so for each row of the forecast report, the first preference that is met will be the displayed rating.
    * Example ratings: Terrible, Bad, Good, Perfect
    * Rating preferences are saved in ratings.json.

### Exiting
* Click the "X" in the top right corner to exit the application.
    * clothing.json and ratings.json is saved and automatically accessed upon reopening the application.

## Features

* Weather Forecast:
    * Fetches weather data using the National Weather Service (NWS) API.
    * Displays temperature, time periods, and conditions.
* Clothing Suggestions:
    * Personalized suggestions based on user-defined preferences for each season.
    * Alerts for temperature transitions during the day.
* Dynamic Location:
    * Use the current location via IP or manually enter a city name.
* Seasonal Theme:
    * Adjusts the interface colors based on the current season.
* Preferences Customization:

## Creators

Pablo Torres, Gayathri Jeyaraman    
The University of Texas at Dallas    
GISC 4317 Final Project
