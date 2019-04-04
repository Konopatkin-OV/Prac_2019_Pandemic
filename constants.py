from PySide2 import QtCore, QtGui
from datetime import date

WINDOW_SIZE = (1200, 600)
WINDOW_START_IDENT = (300, 200)

COUNTRY_SIZE = (500, 500)
COUNTRY_POS = (650, 50)

START_DATE = date(2000, 1, 1)
BASE_SIMULATION_PERIOD = 20 #weeks

CITY_NORMAL_COLOR = QtGui.QColor(50, 200, 50)
CITY_EPIDEMIC_COLOR = QtGui.QColor(200, 50, 50)
CITY_SELECT_COLOR = QtGui.QColor(230, 200, 50)

CITY_MIN_POPULATION = 100
CITY_MAX_POPULATION = 30 * 10**6

CITY_SIZES = [1, 5, 10, 15, 20, 27, 37, 50, 55, 60]

WORKING_PERCENT = 0.65
EPIDEMIC_BORDER = 0.45

INFECTION_DURATION = [0.25, 0.6, 0.15]

CITY_ALPHA = 255
NEW_CITY_ALPHA = 100
