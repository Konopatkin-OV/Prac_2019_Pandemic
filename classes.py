from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QPointF, QRectF
from datetime import date, timedelta
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
        self.set_total_population(1000)

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

        # shift vaccinated
        for i in range(3, 1, -1):
            for j in range(0, 4):
                for k in range(2):
                    src_index = j*8+(i-1)*2+k
                    dst_index = j*8+i*2+k
                    self.population_groups[dst_index] += self.population_groups[src_index]
                    self.population_groups[src_index] = 0

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


    def standard_process(self, cur_month):
        infected = self.get_infected_population()
        total = self.get_total()
        vaccinated = self.get_vaccinated_population()
        new_infected = infected * ((total - vaccinated) / total)
        new_infected *= self.parent_city.transport_density
        new_infected *= CITY_SIZE_INFECT_COEFFICIENTS[self.parent_city.size_type]
        new_infected *= 1 + ((total / CITY_MAX_POPULATION) ** 2) / 10
        new_infected *= MONTH_INFECTION_COEFFICIENTS[cur_month]
        new_infected = int(new_infected * (random() / 4 + (7 / 8)))

        #print(new_infected)

        # test
        # new_infected = int(self.total_population * random() / 3)

        self.infect(new_infected)

    def __str__(self):
        return ((("{} " * 8) + '\n') * 4).format(*self.population_groups)


class City(object):
    def __init__(self):
        self.parent_country = None

        self.population = Population(self)
        self.size_type = 0
        self.r = 10

        self.transport_density = 1.0
        self.is_epidemic = False

        self.vaccination_quota = 0

        self.norm_color = CITY_NORMAL_COLOR
        self.infect_color = CITY_INFECTED_COLOR
        self.epid_color = CITY_EPIDEMIC_COLOR

        self.alpha = 255

        self.pos = QPointF(0, 0)

    def draw(self, painter):
        city_color = self.norm_color if not self.is_epidemic else self.epid_color
        city_color.setAlpha(self.alpha)
        painter.setPen(city_color)
        painter.setBrush(city_color)
        painter.drawEllipse(self.pos, self.r, self.r)
        
        painter.setPen(self.infect_color)
        painter.setBrush(self.infect_color)
        infect_r = self.r * ((self.get_infected() / self.get_population()) ** 0.7)
        painter.drawEllipse(self.pos, infect_r, infect_r)


    def update_size(self):
        self.size_type = 0
        pop = self.population.get_total()
        for border in CITY_SIZE_POPULATION:
            if pop >= border:
                self.size_type += 1
            else:
                break
        self.r = CITY_SIZES[self.size_type]

    def get_radius(self):
        return self.r


    def set_transport_density(self, value):
        self.transport_density = float(value)

    def set_pos(self, value):
        self.pos = QPointF(value)

    def set_population(self, value):
        self.population.set_total_population(int(value))
        self.update_size()
        self.update_epidemic()

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
        self.update_epidemic()
        return infected

    def update_epidemic(self):
        infected = self.population.get_infected_population()
        self.is_epidemic = infected >= self.population.get_total() * EPIDEMIC_BORDER

    def process_time_step(self, cur_month, infection_update_func, funds_quota):
        # must return funds balance delta from current city

        self.population.pass_week()

        vaccinated = self.vaccinate(min(funds_quota, self.vaccination_quota))

        infection_update_func(self.population, cur_month)

        delta_funds = self.parent_country.tax_per_soul * self.population.get_taxable_population()
        delta_funds -= self.parent_country.vaccination_cost * vaccinated
        delta_funds -= self.parent_country.relief_cost * self.population.get_relief_population()

        self.update_epidemic()

        #print(self.population)

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

    def process_time_step(self, cur_month, infection_update_func):
        for city in self.cities:
            self.current_funds += city.process_time_step(cur_month, infection_update_func, 
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
    SimulationState = QtCore.Signal(str)

    def __init__(self, country, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setMouseTracking(True)

        self.country = country

        self.param_labels = []
        self.new_city_labels = []
        self.cur_city_labels = []

        # simulation parameters
        self.simulation_period = BASE_SIMULATION_PERIOD # in weeks
        self.simulation_start_date = START_DATE
        self.infection_update_func = (lambda city: city)

        # city creation parameters
        self.new_city = City()
        self.new_city.set_alpha(NEW_CITY_ALPHA)

        self.new_infect = 0
        self.new_vaccinate = 0

        self.selected_city = None

        self.gui_page = 0

        self.clock_interval = 1000
        self.clock = QtCore.QTimer()
        self.clock.setInterval(1000)
        self.clock.timeout.connect(self.process_time_step)
        self.clock_control_buttons = []

        self.simulating = False
        self.preparing = True
        self.start_time = DEFAULT_START_DATE
        self.time = self.start_time
        self.simulation_duration = 6
        time_delta = timedelta(days=self.simulation_duration * MONTH_DURATION)
        self.finish_time = self.start_time + time_delta

        self.preparation_only_elems = []

        self.bckp_country = deepcopy(country)


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

        if self.gui_page == 1:
            if self.preparing and self.containsNewCity():
                self.new_city.draw(painter)
                if not self.has_space_to_place():
                    pos, r = self.new_city.pos, self.new_city.r

                    new_pen = QtGui.QPen()
                    color = QtGui.QColor(255, 0, 0) # Red
                    new_pen.setColor(color)
                    new_pen.setWidth(3)
                    painter.setPen(new_pen)
                    painter.drawEllipse(pos, r, r)

            values = [self.new_city.get_population(),
                      self.new_infect, 
                      self.new_city.vaccination_quota,
                      self.new_vaccinate,
                      self.new_city.transport_density
                      ]
            names = ["Population", "Infected", "Vaccination quota", "Vaccinated", "Transport density"]
            for name, label, value in zip(names, self.new_city_labels, values):
                label.setText("{}: {}".format(name, value))            
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
                      self.selected_city.vaccination_quota,
                      self.selected_city.get_vaccinated(),
                      self.selected_city.get_immune(),
                      self.selected_city.transport_density
                      ]
            names = ["Population", "Infected", "Vaccination quota", "Vaccinated", "Immune", "Transport density"]
            for name, label, value in zip(names, self.cur_city_labels, values):
                label.setText("{}: {}".format(name, value))

        values = [self.country.get_current_funds(),
                  self.country.get_tax(),
                  self.country.get_vaccination_cost(),
                  self.country.get_relief_cost(),
                  self.clock_interval / 1000,

                  "{} {}".format(MONTHS[self.time.month], self.time.day),
                  sum(map(City.get_population, self.country.cities)),
                  sum(map(City.get_infected, self.country.cities)),
                  sum(map(City.get_vaccinated, self.country.cities)),
                  sum(map(City.get_immune, self.country.cities)),

                  self.simulation_duration
                  ]
        names = ["Current funds", "Taxes per person", "Vaccination cost", "Relief", "Step interval (seconds)",
                 "Current time", "Total population", "Total infected", "Total vaccinated", "Total immune",
                 "Duration (months)"]
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
    def set_cur_city_labels(self, labels):
        self.cur_city_labels = labels

    def set_cur_population(self, amount):
        if self.selected_city is not None and self.preparing:
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

    def set_cur_vaccination_quota(self, quota):
        if self.selected_city is not None:
            self.selected_city.set_vaccination_quota(quota)
        self.repaint()

    def set_cur_transport_density(self, value):
        if self.selected_city is not None:
            self.selected_city.set_transport_density(value)
        self.repaint()

    # new city management
    def set_new_city_labels(self, labels):
        self.new_city_labels = labels

    def set_new_city_population(self, value):
        self.new_city.set_population(value)
        self.repaint()

    def set_new_infect(self, quota):
        self.new_infect = quota
        self.update_new_city()
        self.repaint()

    def set_new_vaccinate(self, quota):
        self.new_vaccinate = quota
        self.update_new_city()
        self.repaint()

    def set_new_vaccination_quota(self, quota):
        self.new_city.set_vaccination_quota(quota)
        self.repaint()

    def set_new_transport_density(self, value):
        self.new_city.set_transport_density(value)
        self.repaint()


    def update_new_city(self):
        self.new_city.set_population(self.new_city.get_population())
        self.new_city.vaccinate(self.new_vaccinate)
        self.new_city.infect(self.new_infect)

    ###
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.remove_city()
        elif event.key() == QtCore.Qt.Key_Space:
            if self.simulating:
                self.stop_simulation()
            else:
                self.start_simulation()
        elif event.key() == QtCore.Qt.Key_Right:
            if not self.simulating:
                self.step_simulation()

    def mousePressEvent(self, event):
        self.setFocus()
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self.gui_page == 1 and self.preparing and self.containsNewCity() :
                if self.has_space_to_place():
                    self.new_city.set_alpha(CITY_ALPHA)
                    self.update_new_city()
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


    def set_infection_func(self, func):
        self.infection_update_func = func

    def gui_page_change(self, value):
        self.gui_page = value
        # self.selected_city = None
        self.repaint()


    def set_clock_control_buttons(self, buttons):
        self.clock_control_buttons = buttons

    def process_time_step(self):
        if self.preparing:
            self.init_simulation()
        self.country.process_time_step(self.time.month, self.infection_update_func)
        if (self.country.current_funds < 0):
            self.finish_simulation()
            self.SimulationState.emit("Simulation finished: flat-broke")
        self.time += SIMULATION_STEP
        if (self.time >= self.finish_time):
            self.finish_simulation()
            self.SimulationState.emit("Simulation finished: time is up")
        self.repaint()

    def set_time_buttons_state(self, states):
        for button, state in zip(self.clock_control_buttons, states):
            button.setEnabled(state)

    def start_simulation(self):
        self.process_time_step()
        self.clock.start()
        self.simulating = True
        self.set_time_buttons_state([False, True, False])

    def stop_simulation(self):
        self.clock.stop()
        self.simulating = False
        self.set_time_buttons_state([True, False, True])

    def step_simulation(self):
        self.stop_simulation()
        self.process_time_step()


    def set_start_month(self, month):
        if self.preparing:
            self.start_time = date(DEFAULT_START_DATE.year, month + 1, DEFAULT_START_DATE.day)
            self.time = self.start_time
        self.repaint()

    def set_simulation_duration(self, duration):
        if self.preparing:
            self.simulation_duration = duration
        self.repaint()


    def set_preparation_only_elems(self, elems):
        self.preparation_only_elems = elems

    def init_simulation(self):
        self.bckp_country = deepcopy(self.country)
        time_delta = timedelta(self.simulation_duration * MONTH_DURATION)
        self.finish_time = self.start_time + time_delta
        self.preparing = False
        self.SimulationState.emit("Simulation in process")
        self.clock_control_buttons[-1].setEnabled(True)

        for elem in self.preparation_only_elems:
            elem.setEnabled(False)

    def finish_simulation(self):
        self.finished = True
        self.stop_simulation()
        self.set_time_buttons_state([False, False, False, True])

    def reset_simulation(self):
        self.preparing = True
        self.finished = False
        self.SimulationState.emit("Preparing for simulation")
        self.stop_simulation()
        self.time = self.start_time
        self.country = deepcopy(self.bckp_country)
        self.set_time_buttons_state([True, False, True, False])

        for elem in self.preparation_only_elems:
            elem.setEnabled(True)

        self.repaint()

