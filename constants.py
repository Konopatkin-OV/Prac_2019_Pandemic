from PySide2 import QtCore, QtGui
from datetime import date, timedelta

WINDOW_SIZE = (1200, 600)
WINDOW_START_IDENT = (300, 200)

COUNTRY_SIZE = (500, 500)
COUNTRY_POS = (650, 50)

START_DATE = date(2000, 1, 1)
BASE_SIMULATION_PERIOD = 20 #weeks

CITY_NORMAL_COLOR = QtGui.QColor(50, 200, 50)
CITY_INFECTED_COLOR = QtGui.QColor(200, 50, 50)
CITY_EPIDEMIC_COLOR = QtGui.QColor(150, 25, 25)
CITY_SELECT_COLOR = QtGui.QColor(230, 200, 50)

CITY_MIN_POPULATION = 100
CITY_MAX_POPULATION = 30 * 10**6

CITY_SIZES = [13, 25, 40]
CITY_SIZE_POPULATION = [2000, 1000000]
CITY_SIZE_INFECT_COEFFICIENTS = [1.0, 1.1, 1.3]

MONTHS = ["Zeromber", "January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]
MONTH_DURATION = 30 # days
MONTH_INFECTION_COEFFICIENTS = [0.0, 1.2, 1.1, 1.0, 0.9, 0.9, 0.8, 0.9, 1.0, 1.1, 1.2, 1.2, 1.2]
DEFAULT_START_DATE = date(2000, 9, 1)
MIN_SIMULATION_DURATION = 6  # months
MAX_SIMULATION_DURATION = 24 # months
SIMULATION_STEP = timedelta(weeks=1)

WORKING_PERCENT = 0.65
EPIDEMIC_BORDER = 0.45

INFECTION_DURATION = [0.25, 0.6, 0.15]

CITY_ALPHA = 255
NEW_CITY_ALPHA = 100
