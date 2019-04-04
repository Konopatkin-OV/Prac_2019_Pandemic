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
        self.population_groups = [0 for i in range(self.N_POP_CATS)]

    def get_total(self):
        return self.total_population

    def get_group(self, mask):
        return sum([self.population_groups[i] for i in range(self.N_POP_CATS) if mask[i]])

    def get_taxable_population(self):
        mask = [(1 - i % 2) * (i < 8) for i in range(self.N_POP_CATS)]
        return self.get_group(mask)

    def get_relief_population(self):
        mask = [(i % 2) * (i > 8) for i in range(self.N_POP_CATS)]
        return self.get_group(mask)

    def get_infected_population(self):
        mask = [(i >= 8) for i in range(self.N_POP_CATS)]
        return self.get_group(mask)

    def get_vaccinated_population(self):
        mask = [(i % 8) >= 2 for i in range(self.N_POP_CATS)]
        return self.get_group(mask)

    def get_immune_population(self):
        mask = [(i % 8) >= 6 for i in range(self.N_POP_CATS)]
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
        #print("PASSING")
        #print(self)
        # shift infected 
        for i in range(3):
            for j in range(0, 8):
                src_index = (i+1)*8+j
                dst_index = i*8+j
                #if i == 0:
                    # now healthy and immune?
                    #dst_index = 6 + j % 2
                self.population_groups[dst_index] += self.population_groups[src_index]
                self.population_groups[src_index] = 0
        #print(self)
        # shift vaccinated
        for i in range(3, 1, -1):
            for j in range(0, 4):
                for k in range(2):
                    src_index = j*8+(i-1)*2+k
                    dst_index = j*8+i*2+k
                    self.population_groups[dst_index] += self.population_groups[src_index]
                    self.population_groups[src_index] = 0
        #print(self)
        #print("PASSED")

    def vaccinate(self, quota):
        # -_-'
        vaccinable_groups = self.population_groups[:2]
        vaccinable = sum(vaccinable_groups)

        quota = min(quota, vaccinable)

        d = random()
        g1 = int(quota * d)
        g2 = quota - g1
        if g1 > vaccinable_groups[0]:
            g2 += g1 - vaccinable_groups[0]
            g1 = vaccinable_groups[0]
        elif g2 > vaccinable_groups[1]:
            g1 += g2 - vaccinable_groups[1]
            g2 = vaccinable_groups[1]

        self.population_groups[0] -= g1
        self.population_groups[1] -= g2

        self.population_groups[2] += g1
        self.population_groups[3] += g2

        return quota

    def infect(self, quota):
        infectable_groups = self.population_groups[:6]
        infectable = sum(infectable_groups)

        quota = min(quota, infectable)

        def get_destribution(n):
            pts = [0] + list(sorted([random() for i in range(n)])) + [1]
            return [pts[i + 1] - pts[i] for i in range(n)]

        # decide who to infect
        group_coeffs = get_destribution(6)
        groups = [int(quota * group_coeffs[i]) for i in range(6)]
        groups[0] += quota - sum(groups)


        good = {i for i in range(6)}
        # check for overflowing and redestribute
        while True:
            for i in range(6):
                if groups[i] > infectable_groups[i]:
                    good -= {i}
                    delta = groups[i] - infectable_groups[i]
                    groups[i] = infectable_groups[i]

                    cur_group_coeffs = get_destribution(len(good))
                    cur_delta = [int(delta * cur_group_coeffs[j]) for j in range(len(good))]
                    cur_delta[0] += delta - sum(cur_delta)
                    for g, j in zip(list(good), range(len(good))):
                        groups[g] += cur_delta[j]
                    break
            else:
                break

        for i in range(6):
            self.population_groups[i] -= groups[i]

        # decide infection duration
        for i in range(6):
            cur_groups = [int(INFECTION_DURATION[j] * groups[i]) for j in range(3)]
            cur_groups[0] += groups[i] - sum(cur_groups)
            for j in range(3):
                self.population_groups[i+(j+1)*8] += cur_groups[j]

        return quota


    def standard_process(self):
        infected = self.get_infected_population()
        new_infected = infected * self.parent_city.transport_density
        new_infected = int(new_infected * (random() / 4 + (7 / 8)))

        print(new_infected)

        # test
        # new_infected = int(self.total_population * random() / 3)

        self.infect(new_infected)

    def __str__(self):
        return ((("{} " * 8) + '\n') * 4).format(*self.population_groups)


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
        self.update_infected()

    def set_alpha(self, value):
        self.alpha = int(value)

    def set_parent(self, country):
        self.parent_country = country

    def get_population(self):
        return self.population.get_total()

    def get_infected(self):
        return self.population.get_infected_population()

    def get_vaccinated(self):
        return self.population.get_vaccinated_population()

    def get_immune(self):
        return self.population.get_immune_population()


    def set_vaccination_quota(self, quota):
        self.vaccination_quota = quota

    def vaccinate(self, quota):
        return self.population.vaccinate(quota)

    def infect(self, quota):
        infected = self.population.infect(quota)
        self.update_infected()
        return infected

    def update_infected(self):
        infected = self.population.get_infected_population()
        self.is_epidemic = infected >= self.population.get_total() * EPIDEMIC_BORDER

    def process_time_step(self, infection_update_func, funds_quota):
        # must return funds balance delta from current city

        self.population.pass_week()

        vaccinated = self.vaccinate(min(funds_quota, self.vaccination_quota))

        infection_update_func(self.population)

        delta_funds = self.parent_country.tax_per_soul * self.population.get_taxable_population()
        delta_funds -= self.parent_country.vaccination_cost * vaccinated
        delta_funds -= self.parent_country.relief_cost * self.population.get_relief_population()

        self.update_infected()

        print(self.population)

        return delta_funds


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
            self.current_funds += city.process_time_step(infection_update_func, 
                                  max(0, int(self.current_funds / self.vaccination_cost)))


    def get_vaccination_cost(self):
        return self.vaccination_cost

    def set_vaccination_cost(self, cost):
        self.vaccination_cost = cost;

    def get_relief_cost(self):
        return self.relief_cost

    def set_relief_cost(self, cost):
        self.relief_cost = cost;

    def get_current_funds(self):
        return self.current_funds

    def set_current_funds(self, funds):
        self.current_funds = funds;

    def get_tax(self):
        return self.tax_per_soul

    def set_tax(self, tax):
        self.tax_per_soul = tax;

###############################################################
class SimulationWidget(QtWidgets.QWidget):
    SelectedCity = QtCore.Signal(bool)
    SelectedCityPopulationChanged = QtCore.Signal(int)

    def __init__(self, country, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setMouseTracking(True)

        self.country = country

        self.param_labels = []
        self.cur_city_labels = []

        # simulation parameters
        self.simulation_period = BASE_SIMULATION_PERIOD # in weeks
        self.simulation_start_date = START_DATE
        self.infection_update_func = (lambda city: city)

        # city creation parameters
        self.new_city = City()
        self.new_city.set_alpha(NEW_CITY_ALPHA)

        self.selected_city = None

        self.gui_page = 0

        self.clock_interval = 1000
        self.clock = QtCore.QTimer()
        self.clock.setInterval(1000)
        self.clock.timeout.connect(self.process_time_step)

        self.simulating = False
        self.time_counter = 0


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
        if self.selected_city is not None:
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

            values = [self.selected_city.get_population(),
                      self.selected_city.get_infected(), 
                      self.selected_city.get_vaccinated(),
                      self.selected_city.get_immune()
                      ]
            names = ["Population", "Infected", "Vaccinated", "Immune"]
            for name, label, value in zip(names, self.cur_city_labels, values):
                label.setText("{}: {}".format(name, value))

        values = [self.country.get_current_funds(),
                  self.country.get_tax(),
                  self.country.get_vaccination_cost(),
                  self.country.get_relief_cost(),
                  self.clock_interval / 1000
                  ]
        names = ["Current funds", "Taxes per person", "Vaccination cost", "Relief", "Step interval (seconds)"]
        for name, label, value in zip(names, self.param_labels, values):
            label.setText("{}: {}".format(name, value))

        painter.end()

    # global params management
    def set_param_labels(self, labels):
        self.param_labels = labels

    def set_current_funds(self, funds):
        self.country.set_current_funds(funds)
        self.repaint()

    def set_tax(self, tax):
        self.country.set_tax(tax)
        self.repaint()

    def set_vaccination_cost(self, cost):
        self.country.set_vaccination_cost(cost)
        self.repaint()

    def set_relief_cost(self, cost):
        self.country.set_relief_cost(cost)
        self.repaint()

    def set_clock_interval(self, delta):
        self.clock_interval = 1000 * delta
        self.clock.setInterval(self.clock_interval)
        self.repaint()

    # selected city params management
    def set_cur_population(self, amount):
        if self.selected_city is not None:
            self.selected_city.set_population(amount)
        self.repaint()

    def infect_cur(self, quota):
        if self.selected_city is not None:
            self.selected_city.infect(quota)
        self.repaint()

    def vaccinate_cur(self, quota):
        if self.selected_city is not None:
            self.selected_city.vaccinate(quota)
        self.repaint()

    def set_vaccination_quota(self, quota):
        if self.selected_city is not None:
            self.selected_city.set_vaccination_quota(quota)
        self.repaint()

    def set_cur_city_labels(self, labels):
        self.cur_city_labels = labels



    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.remove_city()
        elif event.key() == QtCore.Qt.Key_Space:
            if self.simulating:
                self.stop_simulation()
            else:
                self.start_simulation()
        elif event.key() == QtCore.Qt.Key_Right:
            self.step_simulation()

    def mousePressEvent(self, event):
        self.setFocus()
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
        # self.selected_city = None
        self.repaint()

    def process_time_step(self):
        self.country.process_time_step(self.infection_update_func)
        self.time_counter += 1
        self.repaint()

    def start_simulation(self):
        self.process_time_step()
        self.clock.start()
        self.simulating = True

    def stop_simulation(self):
        self.clock.stop()
        self.simulating = False

    def step_simulation(self):
        self.stop_simulation()
        self.process_time_step()
