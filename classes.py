from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QPointF, QRectF
from datetime import date
from copy import deepcopy
from random import random, randrange

from constants import *


class Population(object):
    # Number of population categories
    N_POP_CATS = 32
    # level 1: healthy/infected for 1/2/3 weeks
    # level 2: not vaccinated/vaccinated 1/2/>=3 weeks ago
    # level 3: working/not working

    def __init__(self, parent_city):
        self.parent_city = parent_city

        self.total_population = 0
        self.population_gropus = [0 for i in range(self.N_POP_CATS)]

    def get_total(self):
        return self.total_population

    def get_group(self, mask):
        return sum([self.population_groups[i] for i in range(self.N_POP_CATS) if mask[i]])

    def get_taxable_population(self):
        mask = [(i % 2) * (i < 8) for i in range(self.N_POP_CATS)]
        return self.get_group(mask)

    def get_relief_population(self):
        mask = [(i % 2) * (i > 8) for i in range(self.N_POP_CATS)]
        return self.get_group(mask)

    def set_total_population(self, new_total):
        # reset with all healthy not vaccinated
        self.total_population = int(new_total)
        self.population_groups = [0 for i in range(self.N_POP_CATS)]
        working = int(new_total * WORKING_PERCENT)
        not_working = new_total - working
        self.population_groups[0] = working
        self.population_groups[1] = not_working

    def pass_week(self):
        # shift infected 
        cur = (0, 0)
        for i in range(4):
            for j in range(0, 8):
                self.population_groups[i*8+j] += self.population_groups[(i+1)*8+j]
                self.population_groups[(i+1)*8+j] = 0

        # shift vaccinated
        cur = (0, 0)
        for i in range(3, 0, -1):
            for j in range(0, 4):
                for k in range(2):
                    self.population_groups[j*8+i*2+k] += self.population_groups[j*8+(i-1)*2+k]
                    self.population_groups[j*8+(i-1)*2+k] = 0


class City(object):
    def __init__(self):
        self.parent_country = None

        self.population = Population(self)
        self.r = 10

        self.transport_density = 1.0
        self.is_epidemic = False

        self.vaccination_quota = 0

        self.norm_color = CITY_NORMAL_COLOR
        self.epid_color = CITY_EPIDEMIC_COLOR

        self.alpha = 255

        self.pos = QPointF(0, 0)

    def draw(self, painter):
        city_color = self.norm_color if not self.is_epidemic else self.epid_color
        city_color.setAlpha(self.alpha)
        painter.setPen(city_color)
        painter.setBrush(city_color)
        painter.drawEllipse(self.pos, self.r, self.r)


    def get_radius(self):
        res = 0
        tmp = self.population.get_total()
        while (tmp >= 10):
            tmp /= 10
            res += 1
        return CITY_SIZES[res]


    def set_transport_density(self, value):
        self.transport_density = float(value)

    def set_pos(self, value):
        self.pos = QPointF(value)

    def set_population(self, value):
        self.population.set_total_population(int(value))
        self.r = self.get_radius()

    def set_alpha(self, value):
        self.alpha = int(value)

    def set_parent(self, country):
        self.parent_country = country

    def get_population(self):
        return self.population.get_total()

    def process_time_step(self, infection_update_func):
        # must return funds balance delta from current city
        infection_update_func(self.population)
        return 0.0


class Country(object):
    def __init__(self):
        self.cities = []

        self.vaccination_cost = 0.0
        self.relief_cost = 0.0
        self.current_funds = 0.0
        self.tax_per_soul = 0.0

    def draw(self, painter):
        for city in self.cities:
            city.draw(painter)

    def add_city(self, city):
        self.cities.append(deepcopy(city))
        self.cities[-1].set_parent(self)

    def remove_city(self, city):
        if type(city) == City:
            for i in range(len(self.cities)):
                if self.cities[i] is city:
                    city = i
                    break
        else:
            city = int(city)
        del self.cities[city]

    def check_vicinity(self, pos, r):
        for city in self.cities:
            if QtGui.QVector2D(city.pos - pos).length() < r + city.r:
                return False
        return True

    def find_city(self, pos):
        for city in self.cities:
            if QtGui.QVector2D(city.pos - pos).length() < city.r:
                return city
        return None

    def process_time_step(self, infection_update_func):
        for city in self.cities:
            self.current_funds += city.process_time_step(infection_update_func)

###############################################################
class SimulationWidget(QtWidgets.QWidget):
    SelectedCity = QtCore.Signal(bool)
    SelectedCityPopulationChanged = QtCore.Signal(int)

    def __init__(self, country, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setMouseTracking(True)

        self.country = country

        # simulation parameters
        self.simulation_period = BASE_SIMULATION_PERIOD # in weeks
        self.simulation_start_date = START_DATE
        self.infection_update_func = (lambda city: city)

        # city creation parameters
        self.new_city = City()
        self.new_city.set_alpha(NEW_CITY_ALPHA)

        self.selected_city = None

        self.gui_page = 0

        self.clock = QtCore.QTimer()
        self.clock.setInterval(1000)
        self.clock.timeout.connect(self.process_time_step)


    def containsNewCity(self):
        w, h = self.width(), self.height()
        bounding_rect = QRectF(5, 5, w - 10, h - 10)
        r = self.new_city.get_radius()
        city_rect = QRectF(self.new_city.pos - QPointF(r, r), QtCore.QSize(2*r, 2*r))
        return bounding_rect.contains(city_rect)

    def has_space_to_place(self):
        return self.country.check_vicinity(self.new_city.pos, self.new_city.r)

    def select_city(self, pos):
        self.selected_city = self.country.find_city(pos)
        self.SelectedCity.emit(self.selected_city is not None)
        if self.selected_city is not None:
            self.setFocus()

    def remove_city(self):
        if (self.selected_city is not None):
            self.country.remove_city(self.selected_city)

            self.selected_city = None
            self.SelectedCity.emit(False)
            self.repaint()


    def paintEvent(self, event):
        w, h = self.width(), self.height()
        bounding_rect = QRectF(5, 5, w - 10, h - 10)

        painter = QtGui.QPainter()
        painter.begin(self)

        painter.drawRect(bounding_rect)

        self.country.draw(painter)

        if self.gui_page == 1 and self.containsNewCity():
            self.new_city.draw(painter)
            if not self.has_space_to_place():
                pos, r = self.new_city.pos, self.new_city.r

                new_pen = QtGui.QPen()
                color = QtGui.QColor(255, 0, 0) # Red
                new_pen.setColor(color)
                new_pen.setWidth(3)
                painter.setPen(new_pen)
                painter.drawEllipse(pos, r, r)
        elif self.gui_page == 2 and self.selected_city is not None:
            pos, r = self.selected_city.pos, self.selected_city.r

            new_pen = QtGui.QPen()
            new_pen.setColor(CITY_SELECT_COLOR)
            new_pen.setWidth(3)
            painter.setPen(new_pen)
            painter.setBrush(QtGui.QColor(0, 0, 0, 0))
            painter.drawEllipse(pos, r, r)

            r = min(r / 3, 10)
            painter.setBrush(CITY_SELECT_COLOR)
            painter.drawEllipse(pos, r, r)

        painter.end()

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.StandardKey.Delete):
            self.remove_city()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self.gui_page == 1 and self.containsNewCity():
                if self.has_space_to_place():
                    self.new_city.set_alpha(CITY_ALPHA)
                    self.country.add_city(self.new_city)
                    self.new_city.set_alpha(NEW_CITY_ALPHA)
                    self.repaint()
            elif self.gui_page == 2:
                self.select_city(event.pos())
                self.repaint()

    def mouseMoveEvent(self, event):
        self.new_city.set_pos(QPointF(event.pos()))
        if self.gui_page == 1:
            self.repaint()

    def set_new_city_population(self, value):
        self.new_city.set_population(value)
        self.SelectedCityPopulationChanged.emit(value)
        self.repaint()

    def set_infection_func(self, func):
        self.infection_update_func = func

    def get_new_city_population(self):
        return self.new_city.get_population()

    def gui_page_change(self, value):
        self.gui_page = value
        self.selected_city = None
        self.repaint()

    def process_time_step(self):
        self.country.process_time_step(self.infection_update_func)
        self.repaint()

    def start_simulation(self):
        self.process_time_step()
        self.clock.start()

    def stop_simulation(self):
        self.clock.stop()

    def step_simulation(self):
        self.clock.stop()
        self.process_time_step()
