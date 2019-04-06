# -*- coding: utf-8 -*-

from PySide2 import QtCore, QtGui, QtWidgets
import sys

from classes import *
from constants import *

# returns function from integer which shows all widgets on selected page
# and hides all widgets on other pages
def show_function(pages):
    def res(page):
        page = int(page)
        for i in range(len(pages)):
            if i == page:
                for elem in pages[i]:
                    elem.show()
            else:
                for elem in pages[i]:
                    elem.hide()
    return res


def change_state_func(change_state, parse_input):
    def res():
        args = parse_input()
        if args is not None:
            change_state(args)
    return res


def parse_int_input_func(input_widget, min_val, max_val, output_widget):
    def res():
        val = input_widget.text()
        try:
            val = int(val)
        except:
            output_widget.setText("Input must be an integer")
            return
        if not (min_val <= val <= max_val):
            output_widget.setText("Value must be in [{}, {}] interval".format(min_val, max_val))
            return
        output_widget.setText("")
        return val
    return res


def parse_float_input_func(input_widget, min_val, max_val, output_widget):
    def res():
        val = input_widget.text()
        try:
            val = float(val)
        except:
            output_widget.setText("Input must be a floating point number")
            return
        if not (min_val <= val <= max_val):
            output_widget.setText("Value must be in [{}, {}] interval".format(min_val, max_val))
            return
        output_widget.setText("")
        return val
    return res


def change_text_func(output_widget, template):
    def res(*args):
        output_widget.setText(template.format(*args))
    return res


country = Country()

#########################

cur = City()
for i in range(6,7):
    cur.pos = QtCore.QPointF(60 + 40 * i, 250)
    cur.set_population(10 ** i)
    cur.set_vaccination_quota(10 ** (i - 2))
    cur.population.infect(1 * 10 ** (i - 2))
    cur.set_transport_density(1.1)
    #cur.is_epidemic = i % 2
    #cur.alpha = 255 - (i + 1) * 25
    country.add_city(cur)

country.vaccination_cost = 10.0
country.relief_cost = 10.0
country.current_funds = 10000000.0
country.tax_per_soul = 1.0

#########################

def test_clock_madness(self):
    city = self.parent_city
    country = city.parent_country

    r = randrange(0, 255)
    g = randrange(0, 255)
    b = randrange(0, 255)
    city.norm_color = QtGui.QColor(r, g, b)
    city.r = CITY_SIZES[randrange(2, len(CITY_SIZES))]
    x = randrange(15, COUNTRY_SIZE[0] - 30)
    y = randrange(15, COUNTRY_SIZE[1] - 30)
    city.pos = QPointF(x, y)

    Max = 100
    Speed = 150
    if (randrange(1000) == 0):
        country.add_city(City())
        country.cities = country.cities[:Max]
    simulator.clock.setInterval(len(country.cities) / Max * Speed)

#########################

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
window.setWindowTitle("Pandemic")
window.setGeometry(*WINDOW_START_IDENT, *WINDOW_SIZE)
window.setMinimumSize(*WINDOW_SIZE)
window.setMaximumSize(*WINDOW_SIZE)

baseFont = QtGui.QFont()
baseFont.setPixelSize(20)
baseFont.setWeight(50)

window.setFont(baseFont)

errorFont = QtGui.QFont()
errorFont.setPixelSize(15)
errorFont.setWeight(75)

simulator = SimulationWidget(country, window)
simulator.setGeometry(*COUNTRY_POS, *COUNTRY_SIZE)

simulator.set_infection_func(Population.standard_process)
# test
# simulator.set_infection_func(test_clock_madness)

simulator.new_city.set_pos(QtCore.QPointF(200, 100))
simulator.new_city.set_population(10 ** 3)

###########################################
control_tabs = QtWidgets.QTabWidget(window)
control_tabs.setGeometry(10, 10, 600, 580)
#######################
tab_global = QtWidgets.QWidget()

cur_funds_label = QtWidgets.QLabel(tab_global)
cur_funds_label.setGeometry(25, 10, 300, 40)
cur_funds_label.setText("Current funds: 0")

cur_funds_input = QtWidgets.QLineEdit(tab_global)
cur_funds_input.setGeometry(25, 50, 200, 30)

funds_input_stat_label = QtWidgets.QLabel(tab_global)
funds_input_stat_label.setGeometry(25, 80, 400, 30)
funds_input_stat_label.setText("")
funds_input_stat_label.setFont(errorFont)
funds_input_stat_label.setStyleSheet("QLabel {color: #FF0000}")

cur_funds_input.editingFinished.connect(change_state_func(simulator.set_current_funds, 
    parse_float_input_func(cur_funds_input, 0, 10**12, funds_input_stat_label)))

###

tax_label = QtWidgets.QLabel(tab_global)
tax_label.setGeometry(25, 105, 300, 40)
tax_label.setText("Taxes per person: 0")

tax_input = QtWidgets.QLineEdit(tab_global)
tax_input.setGeometry(25, 145, 200, 30)

tax_input_stat_label = QtWidgets.QLabel(tab_global)
tax_input_stat_label.setGeometry(25, 175, 400, 30)
tax_input_stat_label.setText("")
tax_input_stat_label.setFont(errorFont)
tax_input_stat_label.setStyleSheet("QLabel {color: #FF0000}")

tax_input.editingFinished.connect(change_state_func(simulator.set_tax, 
    parse_float_input_func(tax_input, 0, 1000, tax_input_stat_label)))

###

vaccination_label = QtWidgets.QLabel(tab_global)
vaccination_label.setGeometry(25, 200, 300, 40)
vaccination_label.setText("Vaccination cost: 0")

vaccination_input = QtWidgets.QLineEdit(tab_global)
vaccination_input.setGeometry(25, 240, 200, 30)

vaccination_input_stat_label = QtWidgets.QLabel(tab_global)
vaccination_input_stat_label.setGeometry(25, 270, 400, 30)
vaccination_input_stat_label.setText("")
vaccination_input_stat_label.setFont(errorFont)
vaccination_input_stat_label.setStyleSheet("QLabel {color: #FF0000}")

vaccination_input.editingFinished.connect(change_state_func(simulator.set_vaccination_cost, 
    parse_float_input_func(vaccination_input, 0, 1000, vaccination_input_stat_label)))

###

relief_label = QtWidgets.QLabel(tab_global)
relief_label.setGeometry(25, 295, 300, 40)
relief_label.setText("Relief: 0")

relief_input = QtWidgets.QLineEdit(tab_global)
relief_input.setGeometry(25, 335, 200, 30)

relief_input_stat_label = QtWidgets.QLabel(tab_global)
relief_input_stat_label.setGeometry(25, 365, 400, 30)
relief_input_stat_label.setText("")
relief_input_stat_label.setFont(errorFont)
relief_input_stat_label.setStyleSheet("QLabel {color: #FF0000}")

relief_input.editingFinished.connect(change_state_func(simulator.set_relief_cost, 
    parse_float_input_func(relief_input, 0, 1000, relief_input_stat_label)))

###

speed_label = QtWidgets.QLabel(tab_global)
speed_label.setGeometry(25, 400, 300, 40)
speed_label.setText("Step interval (seconds): 1")

speed_input = QtWidgets.QLineEdit(tab_global)
speed_input.setGeometry(25, 440, 200, 30)

speed_input_stat_label = QtWidgets.QLabel(tab_global)
speed_input_stat_label.setGeometry(25, 470, 400, 30)
speed_input_stat_label.setText("")
speed_input_stat_label.setFont(errorFont)
speed_input_stat_label.setStyleSheet("QLabel {color: #FF0000}")

speed_input.editingFinished.connect(change_state_func(simulator.set_clock_interval, 
    parse_float_input_func(speed_input, 0.01, 5, speed_input_stat_label)))

###

total_population_label = QtWidgets.QLabel(tab_global)
total_population_label.setGeometry(300, 40, 300, 40)
total_population_label.setText("Total population: 0")

total_infected_label = QtWidgets.QLabel(tab_global)
total_infected_label.setGeometry(300, 80, 300, 40)
total_infected_label.setText("Total infected: 0")

total_vaccinated_label = QtWidgets.QLabel(tab_global)
total_vaccinated_label.setGeometry(300, 120, 300, 40)
total_vaccinated_label.setText("Total vaccinated: 0")

total_immune_label = QtWidgets.QLabel(tab_global)
total_immune_label.setGeometry(300, 160, 300, 40)
total_immune_label.setText("Total immune: 0")


time_label = QtWidgets.QLabel(tab_global)
time_label.setGeometry(300, 400, 300, 40)
time_label.setText("Elapsed time: 0")

simulation_reset_button = QtWidgets.QPushButton("Reset simulation", tab_global)
simulation_reset_button.setGeometry(400, 500, 170, 40)
simulation_reset_button.clicked.connect(simulator.reset_simulation)
simulation_reset_button.setEnabled(False)

#####

start_button = QtWidgets.QPushButton("Start", tab_global)
start_button.setGeometry(25, 500, 100, 40)
start_button.clicked.connect(simulator.start_simulation)

pause_button = QtWidgets.QPushButton("Pause", tab_global)
pause_button.setGeometry(145, 500, 100, 40)
pause_button.clicked.connect(simulator.stop_simulation)
pause_button.setEnabled(False)

step_button = QtWidgets.QPushButton("Step", tab_global)
step_button.setGeometry(265, 500, 100, 40)
step_button.clicked.connect(simulator.step_simulation)


simulation_start_label = QtWidgets.QLabel(tab_global)
simulation_start_label.setGeometry(300, 220, 300, 40)
simulation_start_label.setText("Simulation start:")

simulation_start_input = QtWidgets.QComboBox(tab_global)
simulation_start_input.setGeometry(300, 260, 200, 30)
simulation_start_input.addItems(MONTHS[1:])
simulation_start_input.setCurrentIndex(8)
QtCore.QObject.connect(simulation_start_input, QtCore.SIGNAL("currentIndexChanged(int)"),
                       simulator.set_start_month)


simulator.set_clock_control_buttons([start_button, pause_button, step_button, simulation_reset_button])


simulation_duration_label = QtWidgets.QLabel(tab_global)
simulation_duration_label.setGeometry(300, 295, 300, 40)
simulation_duration_label.setText("Duration (months): 0")

simulation_duration_input = QtWidgets.QLineEdit(tab_global)
simulation_duration_input.setGeometry(300, 335, 200, 30)

simulation_duration_input_stat_label = QtWidgets.QLabel(tab_global)
simulation_duration_input_stat_label.setGeometry(300, 365, 400, 30)
simulation_duration_input_stat_label.setText("")
simulation_duration_input_stat_label.setFont(errorFont)
simulation_duration_input_stat_label.setStyleSheet("QLabel {color: #FF0000}")

simulation_duration_input.editingFinished.connect(change_state_func(simulator.set_simulation_duration, 
    parse_int_input_func(simulation_duration_input, 
                         MIN_SIMULATION_DURATION, MAX_SIMULATION_DURATION, 
                         simulation_duration_input_stat_label)))


simulator.set_param_labels([cur_funds_label, tax_label, vaccination_label, relief_label, speed_label, time_label, 
                            total_population_label, total_infected_label, total_vaccinated_label, total_immune_label,
                            simulation_duration_label])

simulation_finish_label = QtWidgets.QLabel(tab_global)
simulation_finish_label.setGeometry(300, 430, 250, 40)
simulation_finish_label.setText("Preparing for simulation")
simulation_finish_label.setFont(errorFont)
simulation_finish_label.setStyleSheet("QLabel {color: #FF0000}")

simulator.SimulationState.connect(simulation_finish_label.setText)

control_tabs.addTab(tab_global, "Simulation")
##########################################################
tab_create_city = QtWidgets.QWidget()

new_city_pop_label = QtWidgets.QLabel(tab_create_city)
new_city_pop_label.setGeometry(10, 10, 300, 30)
new_city_pop_label.setText("Total population:")

new_city_pop_input = QtWidgets.QLineEdit(tab_create_city)
new_city_pop_input.setGeometry(310, 10, 150, 30)

new_city_pop_button = QtWidgets.QPushButton(tab_create_city)
new_city_pop_button.setText("Apply")
new_city_pop_button.setGeometry(470, 10, 100, 30)

new_city_pop_stat_label = QtWidgets.QLabel(tab_create_city)
new_city_pop_stat_label.setGeometry(310, 40, 350, 30)
new_city_pop_stat_label.setText("")
new_city_pop_stat_label.setFont(errorFont)
new_city_pop_stat_label.setStyleSheet("QLabel {color: #FF0000}")

new_city_pop_button.pressed.connect(change_state_func(simulator.set_new_city_population, 
    parse_int_input_func(new_city_pop_input, CITY_MIN_POPULATION, CITY_MAX_POPULATION, new_city_pop_stat_label)))


new_city_infected_label = QtWidgets.QLabel(tab_create_city)
new_city_infected_label.setGeometry(10, 70, 300, 30)
new_city_infected_label.setText("Infected population:")

new_city_infect_input = QtWidgets.QLineEdit(tab_create_city)
new_city_infect_input.setGeometry(310, 70, 150, 30)

new_city_infect_button = QtWidgets.QPushButton(tab_create_city)
new_city_infect_button.setText("Apply")
new_city_infect_button.setGeometry(470, 70, 100, 30)

new_city_infect_stat_label = QtWidgets.QLabel(tab_create_city)
new_city_infect_stat_label.setGeometry(310, 100, 350, 30)
new_city_infect_stat_label.setText("")
new_city_infect_stat_label.setFont(errorFont)
new_city_infect_stat_label.setStyleSheet("QLabel {color: #FF0000}")

new_city_infect_button.pressed.connect(change_state_func(simulator.set_new_infect, 
    parse_int_input_func(new_city_infect_input, 1, CITY_MAX_POPULATION, new_city_infect_stat_label)))


new_city_quota_label = QtWidgets.QLabel(tab_create_city)
new_city_quota_label.setGeometry(10, 130, 300, 30)
new_city_quota_label.setText("Vaccination quota:")

new_city_set_quota_input = QtWidgets.QLineEdit(tab_create_city)
new_city_set_quota_input.setGeometry(310, 130, 150, 30)

new_city_set_quota_button = QtWidgets.QPushButton(tab_create_city)
new_city_set_quota_button.setText("Apply")
new_city_set_quota_button.setGeometry(470, 130, 100, 30)

new_city_set_quota_stat_label = QtWidgets.QLabel(tab_create_city)
new_city_set_quota_stat_label.setGeometry(310, 160, 350, 30)
new_city_set_quota_stat_label.setText("")
new_city_set_quota_stat_label.setFont(errorFont)
new_city_set_quota_stat_label.setStyleSheet("QLabel {color: #FF0000}")

new_city_set_quota_button.pressed.connect(change_state_func(simulator.set_new_vaccination_quota, 
    parse_int_input_func(new_city_set_quota_input, 0, CITY_MAX_POPULATION, new_city_set_quota_stat_label)))


new_city_vaccinated_label = QtWidgets.QLabel(tab_create_city)
new_city_vaccinated_label.setGeometry(10, 190, 300, 30)
new_city_vaccinated_label.setText("Vaccinated population:")

new_city_vaccinate_input = QtWidgets.QLineEdit(tab_create_city)
new_city_vaccinate_input.setGeometry(310, 190, 150, 30)

new_city_vaccinate_button = QtWidgets.QPushButton(tab_create_city)
new_city_vaccinate_button.setText("Apply")
new_city_vaccinate_button.setGeometry(470, 190, 100, 30)

new_city_vaccinate_stat_label = QtWidgets.QLabel(tab_create_city)
new_city_vaccinate_stat_label.setGeometry(310, 220, 350, 30)
new_city_vaccinate_stat_label.setText("")
new_city_vaccinate_stat_label.setFont(errorFont)
new_city_vaccinate_stat_label.setStyleSheet("QLabel {color: #FF0000}")

new_city_vaccinate_button.pressed.connect(change_state_func(simulator.set_new_vaccinate, 
    parse_int_input_func(new_city_vaccinate_input, 1, CITY_MAX_POPULATION, new_city_vaccinate_stat_label)))


new_city_transport_density_label = QtWidgets.QLabel(tab_create_city)
new_city_transport_density_label.setGeometry(10, 250, 300, 30)
new_city_transport_density_label.setText("Transport density:")

new_city_transport_density_input = QtWidgets.QLineEdit(tab_create_city)
new_city_transport_density_input.setGeometry(310, 250, 150, 30)

new_city_transport_density_button = QtWidgets.QPushButton(tab_create_city)
new_city_transport_density_button.setText("Apply")
new_city_transport_density_button.setGeometry(470, 250, 100, 30)

new_city_transport_density_stat_label = QtWidgets.QLabel(tab_create_city)
new_city_transport_density_stat_label.setGeometry(310, 280, 350, 30)
new_city_transport_density_stat_label.setText("")
new_city_transport_density_stat_label.setFont(errorFont)
new_city_transport_density_stat_label.setStyleSheet("QLabel {color: #FF0000}")

new_city_transport_density_button.pressed.connect(change_state_func(simulator.set_new_transport_density, 
    parse_float_input_func(new_city_transport_density_input, 0.0, 5.0, new_city_transport_density_stat_label)))

simulator.set_new_city_labels([new_city_pop_label, new_city_infected_label, new_city_quota_label, 
                               new_city_vaccinated_label, new_city_transport_density_label])

control_tabs.addTab(tab_create_city, "Create City")
##########################################################
tab_manage_city = QtWidgets.QWidget()

idle_label = QtWidgets.QLabel(tab_manage_city)
idle_label.setGeometry(100, 10, 200, 40)
idle_label.setText("Please, select a city")

city_pop_label = QtWidgets.QLabel(tab_manage_city)
city_pop_label.setGeometry(10, 10, 300, 30)
city_pop_label.setText("Total population:")

city_pop_input = QtWidgets.QLineEdit(tab_manage_city)
city_pop_input.setGeometry(310, 10, 150, 30)

city_pop_button = QtWidgets.QPushButton(tab_manage_city)
city_pop_button.setText("Reset")
city_pop_button.setGeometry(470, 10, 100, 30)

city_pop_stat_label = QtWidgets.QLabel(tab_manage_city)
city_pop_stat_label.setGeometry(310, 40, 350, 30)
city_pop_stat_label.setText("")
city_pop_stat_label.setFont(errorFont)
city_pop_stat_label.setStyleSheet("QLabel {color: #FF0000}")

city_pop_button.pressed.connect(change_state_func(simulator.set_cur_population, 
    parse_int_input_func(city_pop_input, CITY_MIN_POPULATION, CITY_MAX_POPULATION, city_pop_stat_label)))


city_infected_label = QtWidgets.QLabel(tab_manage_city)
city_infected_label.setGeometry(10, 70, 300, 30)
city_infected_label.setText("Infected population:")

city_infect_input = QtWidgets.QLineEdit(tab_manage_city)
city_infect_input.setGeometry(310, 70, 150, 30)

city_infect_button = QtWidgets.QPushButton(tab_manage_city)
city_infect_button.setText("Infect")
city_infect_button.setGeometry(470, 70, 100, 30)

city_infect_stat_label = QtWidgets.QLabel(tab_manage_city)
city_infect_stat_label.setGeometry(310, 100, 350, 30)
city_infect_stat_label.setText("")
city_infect_stat_label.setFont(errorFont)
city_infect_stat_label.setStyleSheet("QLabel {color: #FF0000}")

city_infect_button.pressed.connect(change_state_func(simulator.infect_cur, 
    parse_int_input_func(city_infect_input, 1, CITY_MAX_POPULATION, city_infect_stat_label)))


city_quota_label = QtWidgets.QLabel(tab_manage_city)
city_quota_label.setGeometry(10, 130, 300, 30)
city_quota_label.setText("Vaccination quota:")

city_set_quota_input = QtWidgets.QLineEdit(tab_manage_city)
city_set_quota_input.setGeometry(310, 130, 150, 30)

city_set_quota_button = QtWidgets.QPushButton(tab_manage_city)
city_set_quota_button.setText("Apply")
city_set_quota_button.setGeometry(470, 130, 100, 30)

city_set_quota_stat_label = QtWidgets.QLabel(tab_manage_city)
city_set_quota_stat_label.setGeometry(310, 160, 350, 30)
city_set_quota_stat_label.setText("")
city_set_quota_stat_label.setFont(errorFont)
city_set_quota_stat_label.setStyleSheet("QLabel {color: #FF0000}")

city_set_quota_button.pressed.connect(change_state_func(simulator.set_cur_vaccination_quota, 
    parse_int_input_func(city_set_quota_input, 0, CITY_MAX_POPULATION, city_set_quota_stat_label)))


city_vaccinated_label = QtWidgets.QLabel(tab_manage_city)
city_vaccinated_label.setGeometry(10, 190, 300, 30)
city_vaccinated_label.setText("Vaccinated population:")

city_vaccinate_input = QtWidgets.QLineEdit(tab_manage_city)
city_vaccinate_input.setGeometry(310, 190, 150, 30)

city_vaccinate_button = QtWidgets.QPushButton(tab_manage_city)
city_vaccinate_button.setText("Vaccinate")
city_vaccinate_button.setGeometry(470, 190, 100, 30)

city_vaccinate_stat_label = QtWidgets.QLabel(tab_manage_city)
city_vaccinate_stat_label.setGeometry(310, 220, 350, 30)
city_vaccinate_stat_label.setText("")
city_vaccinate_stat_label.setFont(errorFont)
city_vaccinate_stat_label.setStyleSheet("QLabel {color: #FF0000}")

city_vaccinate_button.pressed.connect(change_state_func(simulator.vaccinate_cur, 
    parse_int_input_func(city_vaccinate_input, 1, CITY_MAX_POPULATION, city_vaccinate_stat_label)))

city_immune_label = QtWidgets.QLabel(tab_manage_city)
city_immune_label.setGeometry(10, 250, 300, 30)
city_immune_label.setText("Immune population:")


city_transport_density_label = QtWidgets.QLabel(tab_manage_city)
city_transport_density_label.setGeometry(10, 310, 300, 30)
city_transport_density_label.setText("Transport density:")

city_transport_density_input = QtWidgets.QLineEdit(tab_manage_city)
city_transport_density_input.setGeometry(310, 310, 150, 30)

city_transport_density_button = QtWidgets.QPushButton(tab_manage_city)
city_transport_density_button.setText("Apply")
city_transport_density_button.setGeometry(470, 310, 100, 30)

city_transport_density_stat_label = QtWidgets.QLabel(tab_manage_city)
city_transport_density_stat_label.setGeometry(310, 340, 350, 30)
city_transport_density_stat_label.setText("")
city_transport_density_stat_label.setFont(errorFont)
city_transport_density_stat_label.setStyleSheet("QLabel {color: #FF0000}")

city_transport_density_button.pressed.connect(change_state_func(simulator.set_cur_transport_density, 
    parse_float_input_func(city_transport_density_input, 0.0, 5.0, city_transport_density_stat_label)))


simulator.set_cur_city_labels([city_pop_label, city_infected_label, city_quota_label, 
                               city_vaccinated_label, city_immune_label, city_transport_density_label])

delete_city_button = QtWidgets.QPushButton("Annihilate city", tab_manage_city)
delete_city_button.setGeometry(100, 400, 200, 40)

delete_city_button.clicked.connect(simulator.remove_city)

elems = [city_pop_label, city_infected_label, city_quota_label, 
         city_vaccinated_label, city_immune_label, city_transport_density_label,
         city_pop_input, city_pop_button, city_pop_stat_label,
         city_infect_input, city_infect_button, city_infect_stat_label,
         city_set_quota_input, city_set_quota_button, city_set_quota_stat_label,
         city_transport_density_input, city_transport_density_button, city_transport_density_stat_label,
         city_vaccinate_input, city_vaccinate_button, city_vaccinate_stat_label,
         delete_city_button]
for elem in elems:
    elem.hide()

simulator.SelectedCity.connect(show_function([[idle_label], elems]))

control_tabs.addTab(tab_manage_city, "Manage City")
###########################################
simulator.set_preparation_only_elems([simulation_start_input, city_pop_input, city_pop_button, 
                                      tab_create_city, cur_funds_input])


QtCore.QObject.connect(control_tabs, QtCore.SIGNAL("currentChanged(int)"),
                       simulator.gui_page_change)

window.show()
app.exec_()


#+ github
#-> alesapin@gmail.com

# TODO: 
# DONE: прикрутить даты и сезонность (начало и конец)
# DONE: прикрутить таки типы городов и заражать в зависимости от типа + процентно пропорционально населению
# DONE: блокировать кнопки pause и step в соответствующих ситуациях
# DONE: глобальный reset
# DONE: нельзя добавлять города в течение симуляции

# bonus: добавить автоматический выбор квоты на вакцинацию
# bonusbonus: сохранение?
