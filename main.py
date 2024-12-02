import os
import sys

from WBWorldGenerator import Robot
from QtGui import MainUi
from PyQt5.QtWidgets import QApplication
import shared_data
shared_data.create_shared_data()

r'''
deprecated
def ui_to_py():
    ui_filename = r'"C:\Users\toupa\Desktop\ESE - S1\PFE\Simulation_files\ui_files\window_0_1.ui"'
    py_filename = r'"C:\Users\toupa\Desktop\ESE - S1\PFE\Simulation_files\ui_files\window_0_1.py"'
    os.system(f"pyuic5 {ui_filename} -o {py_filename}")'''


if __name__ == '__main__':
    # TODO: create data permanence
    # TODO: modify wbt file from cell editor

    # TODO: regarding the feedback, if the package is moved out, automatically move the start cell to
    app = QApplication(sys.argv)
    r = Robot(translation=[0, 0, 0.1], dimensions=[5, 5], rotation=[0, 0, 1, 0], controller=r'cell_controller_0_3')
    ui = MainUi(r)
    ui.show()
    app.exec_()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
