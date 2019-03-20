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
for i in range(10):
    cur.pos = QtCore.QPointF(60 + 40 * i, 250)
    cur.set_population(10 ** i)
    cur.is_epidemic = i % 2
    cur.alpha = 255 - (i + 1) * 25
    country.add_city(cur)

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

simulator.new_city.set_pos(QtCore.QPointF(200, 100))
simulator.new_city.set_population(10 ** 3)

###########################################
control_tabs = QtWidgets.QTabWidget(window)
control_tabs.setGeometry(10, 10, 400, 580)
########
tab_global = QtWidgets.QWidget()

label = QtWidgets.QLabel(tab_global)
label.setGeometry(10, 10, 300, 100)
label.setText("Page 1\n[line 2]")

control_tabs.addTab(tab_global, "Simulation")
########
tab_create_city = QtWidgets.QWidget()

population_label = QtWidgets.QLabel(tab_create_city)
population_label.setGeometry(10, 10, 200, 30)
population_label.setText("Population: {}".format(simulator.get_new_city_population()))

simulator.SelectedCityPopulationChanged.connect(change_text_func(population_label, "Population: {}"))

population_input = QtWidgets.QLineEdit(tab_create_city)
population_input.setGeometry(10, 50, 200, 30)

input_stat_label = QtWidgets.QLabel(tab_create_city)
input_stat_label.setGeometry(10, 80, 400, 30)
input_stat_label.setText("")
input_stat_label.setFont(errorFont)
input_stat_label.setStyleSheet("QLabel {color: #FF0000}")

population_input.editingFinished.connect(change_state_func(simulator.set_new_city_population, 
    parse_int_input_func(population_input, CITY_MIN_POPULATION, CITY_MAX_POPULATION, input_stat_label)))

control_tabs.addTab(tab_create_city, "Create City")
########
tab_manage_city = QtWidgets.QWidget()

label = QtWidgets.QLabel(tab_manage_city)
label.setGeometry(100, 10, 200, 50)
label.setText("Please, select a city")

delete_city_button = QtWidgets.QPushButton("Annihilate city", tab_manage_city)
delete_city_button.setGeometry(100, 400, 200, 40)
delete_city_button.hide()

delete_city_button.clicked.connect(simulator.remove_city)

simulator.SelectedCity.connect(show_function([[label], [delete_city_button]]))

control_tabs.addTab(tab_manage_city, "Manage City")
###########################################


QtCore.QObject.connect(control_tabs, QtCore.SIGNAL("currentChanged(int)"),
                       simulator.gui_page_change)

# QtCore.QTimer

#SpinBox = QtWidgets.QSpinBox(Window)
#SpinBox.setGeometry(220, 50, 100, 30)
#SpinBox.setMaximum(DEPTHS["Кривая Коха"])
#SpinBox.setFont(BaseFont)
#ComboBox = QtWidgets.QComboBox(Window)
#for i in range(len(FRACTALS)):
    #ComboBox.insertItem(i, FRACTALS[i])
#ComboBox.setGeometry(10, 50, 210, 30)
#
#QtCore.QObject.connect(SpinBox, QtCore.SIGNAL("valueChanged(int)"),
                       #Window.FractalWidget.setValue)
#QtCore.QObject.connect(ComboBox, QtCore.SIGNAL("currentIndexChanged(int)"),
                       #Window.FractalWidget.setType)
window.show()
app.exec_()


#+ github
#-> alesapin@gmail.com
