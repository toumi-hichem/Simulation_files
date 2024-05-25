import math
import os
import sys

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QBrush, QPen, QPolygonF, QColor
from math import cos, sin
from WBWorldGenerator import Robot
from QtGui import MainUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, \
    QGraphicsPolygonItem, QGraphicsLineItem
import shared_data

shared_data.create_shared_data()

r'''
deprecated
def ui_to_py():
    ui_filename = r'"C:\Users\toupa\Desktop\ESE - S1\PFE\Simulation_files\ui_files\window_0_1.ui"'
    py_filename = r'"C:\Users\toupa\Desktop\ESE - S1\PFE\Simulation_files\ui_files\window_0_1.py"'
    os.system(f"pyuic5 {ui_filename} -o {py_filename}")'''


class Hexagon(QGraphicsPolygonItem):
    # TODO: option to remake one cell at a time
    def __init__(self, center_x, center_y, vector_dir=math.pi, show_arrows=True, highligh=0, hex_size=40, *__args):
        super().__init__(*__args)  # TODO: set obstacle/highlight/selected priorities
        # Hexagon
        self._arrow = []
        self.hex_size = hex_size
        self.center_x = center_x
        self.center_y = center_y
        self.brush = None
        self.pen = None
        self._highlight = highligh
        self._selected = False
        self._obstacle = 0

        # Styles
        self.default_brush = QBrush(QColor("dark blue"))
        self.default_pen = QPen(QColor("aqua"))

        self.highlight_brush = QBrush(QColor("lightblue"))
        self.highlight_pen = QPen(QColor("white"))

        self.vector_pen = QPen(QColor("yellow"))

        self.select_brush = QBrush(QColor("orange"))
        self.select_pen = QPen(QColor("white"))

        self.obstacle_brush = QBrush(QColor("grey"))
        self.obstacle_pen = QPen(QColor("white"))

        self.start_brush = QBrush(QColor("light green"))
        self.start_pen = QPen(QColor("while"))

        self.end_brush = QBrush(QColor("red"))
        self.end_pen = QPen(QColor("orange"))

        # Vectors
        self.vector_length = self.hex_size / 2
        self.vector_dir = vector_dir
        self.show_arrows = show_arrows

        self._core = self.create()
        self.setPolygon(self._core)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)

        self.style_hex()
        self.create_arrow()

        self._content = [self, ] + self._arrow
        self.is_hovered = False

    def create(self):
        points = []
        for i in range(6):
            angle_deg = 60 * i + 30
            angle_rad = math.radians(angle_deg)
            x = self.center_x + self.hex_size * math.cos(angle_rad)
            y = self.center_y + self.hex_size * math.sin(angle_rad)
            points.append(QPointF(x, y))
        return QPolygonF(points)

    def style_hex(self):
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)

    def create_arrow(self, vector_dir=None):
        if not vector_dir:
            vector_dir = self.vector_dir
        if not self.show_arrows or vector_dir is None:
            self._arrow = []
            self._content = [self, ] + self._arrow
            return None
        self.style_arrow()
        vec_x_end = self.center_x + self.vector_length * math.cos(vector_dir)
        vec_y_end = self.center_y + self.vector_length * sin(vector_dir)
        line = QGraphicsLineItem(self.center_x, self.center_y, vec_x_end, vec_y_end)

        arrow_angle = vector_dir + math.pi * (3 / 4)
        arrow_right = QGraphicsLineItem(vec_x_end, vec_y_end,
                                        vec_x_end + ((self.vector_length / 2) * cos(arrow_angle)),
                                        vec_y_end + ((self.vector_length / 2) * sin(arrow_angle)))
        arrow_angle -= math.pi * (3 / 4) * 2
        arrow_left = QGraphicsLineItem(vec_x_end, vec_y_end,
                                       vec_x_end + ((self.vector_length / 2) * cos(arrow_angle)),
                                       vec_y_end + ((self.vector_length / 2) * sin(arrow_angle)))

        line.setPen(self.vector_pen)
        arrow_left.setPen(self.vector_pen)
        arrow_right.setPen(self.vector_pen)
        self._arrow = [line, arrow_left, arrow_right]
        self._content = [self, ] + self._arrow

    def style_arrow(self):
        self.vector_pen = QPen(QColor("yellow"))

    def specific_highlight(self, s_e):
        if self.highlight:
            self.setBrush(self.default_brush)
            self.setPen(self.default_pen)
            self.highlight = 0
        else:
            self.highlight = 1
            if s_e == 'start':
                self.setBrush(self.start_brush)
                self.setPen(self.start_pen)
            elif s_e == 'end':
                self.setBrush(self.end_brush)
                self.setPen(self.end_pen)

    @property
    def content(self):
        return self._content

    @property
    def highlight(self):
        return self._highlight

    @property
    def selected(self):
        return self._selected

    @property
    def obstacle(self):
        return self._obstacle

    @highlight.setter
    def highlight(self, value):
        self._highlight = value

    @selected.setter
    def selected(self, value):
        self._selected = value
        if self._selected:
            self.setBrush(self.select_brush)
            self.setPen(self.select_pen)
        else:
            self.setBrush(self.default_brush)
            self.setPen(self.default_pen)

    @obstacle.setter
    def obstacle(self, value: int):

        self._obstacle = 1 if value else 0
        if self._obstacle:
            self.setBrush(self.obstacle_brush)
            self.setPen(self.obstacle_pen)
        else:
            self.setBrush(self.default_brush)
            self.setPen(self.default_pen)


class test_class(QMainWindow):
    hex_size = 80
    x_cell_dist = hex_size * 1.73#* cos(math.radians(30))
    y_cell_dist = hex_size * 1.5#* sin(math.radians(30))
    def __init__(self):
        super(test_class, self).__init__()
        self.col_count = 4
        self.row_count = 4
        view = QGraphicsView()
        scene = QGraphicsScene()
        positions = self.create_cells()
        for j in range(self.col_count):
            for i in range(self.row_count):
                hexagon = Hexagon(center_x=positions[i][j][0], center_y=positions[i][j][1], hex_size=self.hex_size)
                scene.addItem(hexagon)
        view.setScene(scene)
        self.setCentralWidget(view)

    def create_cells(self):
        positions = []
        for i in range(self.row_count):
            positions.append([])
            for j in range(self.col_count):
                center_y = self.y_cell_dist * i #+ (self.hex_size * 0.9 if j % 2 == 0 else 0)
                center_x = self.x_cell_dist * j + (self.hex_size * 0.9 if i % 2 == 0 else 0)
                positions[i].append([center_x, center_y])
        return positions

    def create_hexagon(self, center_x, center_y):
        points = []
        for i in range(6):
            angle_deg = 60 * i + 30
            angle_rad = math.radians(angle_deg)
            x = center_x + self.hex_size * cos(angle_rad)
            y = center_y + self.hex_size * sin(angle_rad)
            points.append(QPointF(x, y))
        return QPolygonF(points)


if __name__ == '__main__':
    # TODO: create data permanence
    # TODO: modify wbt file from cell editor

    # TODO: regarding the feedback, if the package is moved out, automatically move the start cell to
    '''app = QApplication(sys.argv)
    r = Robot(translation=[0, 0, 0.1], dimensions=[5, 5], rotation=[0, 0, 1, 0], controller=r'<extern>')
    ui = test_class()
    ui.show()
    app.exec_()'''

    grid = [[0, 1, 0, 0, 1, 0], [0, 0, 0, 1, 0, 0]]

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
