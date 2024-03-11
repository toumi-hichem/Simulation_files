import os
import sys

from WBWorldGenerator import Robot
from QtGui import MainUi
from PyQt5.QtWidgets import QApplication


r'''
deprecated
def ui_to_py():
    ui_filename = r'"C:\Users\toupa\Desktop\ESE - S1\PFE\Simulation_files\ui_files\window_0_1.ui"'
    py_filename = r'"C:\Users\toupa\Desktop\ESE - S1\PFE\Simulation_files\ui_files\window_0_1.py"'
    os.system(f"pyuic5 {ui_filename} -o {py_filename}")'''


if __name__ == '__main__':
    #r = Robot(translation=[0, 0, 0.1], dimensions=[5, 5], rotation=[0, 0, 1, 0], controller=r'<extern>')
    #r.create_file()
    #print(r)
    app = QApplication(sys.argv)
    r = Robot(translation=[0, 0, 0.1], dimensions=[5, 5], rotation=[0, 0, 1, 0], controller=r'<extern>')
    ui = MainUi(r)
    ui.show()
    app.exec_()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
