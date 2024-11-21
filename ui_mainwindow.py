from PyQt5 import QtCore, QtWidgets


class Ui_MainWindow():
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(500, 400)

        self.weather_button = QtWidgets.QPushButton(MainWindow)
        self.weather_button.setGeometry(QtCore.QRect(60, 50, 150, 30))
        self.weather_button.setObjectName("weather_button")

        self.status_label = QtWidgets.QLabel(MainWindow)
        self.status_label.setGeometry(QtCore.QRect(60, 100, 400, 30))
        self.status_label.setObjectName("status_label")

        # Ideal Weather Input
        self.ideal_temp_input = QtWidgets.QLineEdit(MainWindow)
        self.ideal_temp_input.setGeometry(QtCore.QRect(60, 150, 100, 30))
        self.ideal_temp_input.setPlaceholderText("Ideal Temp (°F)")

        self.ideal_wind_input = QtWidgets.QLineEdit(MainWindow)
        self.ideal_wind_input.setGeometry(QtCore.QRect(180, 150, 100, 30))
        self.ideal_wind_input.setPlaceholderText("Ideal Wind (mph)")
      
        self.check_weather_button = QtWidgets.QPushButton(MainWindow)
        self.check_weather_button.setGeometry(QtCore.QRect(60, 200, 150, 30))
        self.check_weather_button.setObjectName("check_weather_button")

        self.ideal_weather_label = QtWidgets.QLabel(MainWindow)  # New label for ideal weather results
        self.ideal_weather_label.setGeometry(QtCore.QRect(60, 250, 400, 60))  # Positioned below the button
        self.ideal_weather_label.setWordWrap(True)
        self.ideal_weather_label.setObjectName("ideal_weather_label")
        self.exit_button = QtWidgets.QPushButton(MainWindow)  # Added Exit Button
        self.exit_button.setGeometry(QtCore.QRect(250, 200, 150, 30))
        self.exit_button.setObjectName("exit_button")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.exit_button.clicked.connect(MainWindow.close)  # Connect Exit Button

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Weather and KML Map"))
        self.weather_button.setText(_translate("MainWindow", "Get Weather Data"))
        self.status_label.setText(_translate("MainWindow", "Status: Ready"))
        self.check_weather_button.setText(_translate("MainWindow", "Check Ideal Weather"))
        self.exit_button.setText(_translate("MainWindow", "Exit"))  # Set Exit Button Text
