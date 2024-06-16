import math
import os
import subprocess
from shared_data import SharedData, shared_mem
from loggerClass import logger
from math import cos, sin, radians
import numpy as np
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QSizePolicy, QListView, QGraphicsPixmapItem, QComboBox, \
    QProgressBar, QTabWidget, QLineEdit
import sys
from WBWorldGenerator import Robot
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsView, QVBoxLayout, QPushButton, QSpinBox, \
    QLabel, QGraphicsLineItem, QHBoxLayout, QGraphicsRectItem, QFileDialog, QStackedWidget, QGraphicsPolygonItem, \
    QGraphicsItemGroup
from PyQt5.QtGui import QBrush, QPen, QPolygonF, QPainter, QImage, QPixmap, QPainterPath, QColor, QStandardItem, \
    QStandardItemModel, QCursor, QGuiApplication, QTransform
from PyQt5.QtCore import Qt, QPointF, QLineF, QEvent, QRectF, pyqtSlot, QPropertyAnimation, QAbstractAnimation, \
    QEasingCurve, QTimer, QPoint
from PathFinding import CelluvoyerGrid
from QtUtilities import FoldableToolBar, Package, LaneGraphicRepresentation


# TODO: Create a cell editor table for color, dimensions ....
# TODO: Write a setup.
# TODO: maybe even exclude individual engines if not inside bounds to save energy, need hexagon class
# TODO: Handle multiple packages

# shared mem:


class Hexagon(QGraphicsPolygonItem):
    # TODO: option to remake one cell at a time
    def __init__(self, center_x, center_y, vector_dir: list | None = None, show_arrows=True, highligh=0, hex_size=40,
                 i=None, j=None, arrow_color=None, *__args):
        super().__init__(*__args)  # TODO: set obstacle/highlight/selected priorities
        # Hexagon
        self.i = i
        self.j = j
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

        self.vector_pen = QPen(QColor(arrow_color))

        self.select_brush = QBrush(QColor("orange"))
        self.select_pen = QPen(QColor("white"))

        self.obstacle_brush = QBrush(QColor("grey"))
        self.obstacle_pen = QPen(QColor("white"))

        self.start_brush = QBrush(QColor("light green"))
        self.start_pen = QPen(QColor("while"))

        self.end_brush = QBrush(QColor("red"))
        self.end_pen = QPen(QColor("orange"))

        self.ON_pen = QPen(QColor("light green"))
        self.ON_brush = QBrush(QColor("light green"))

        self.OFF_pen = QPen(QColor("red"))
        self.OFF_brush = QBrush(QColor("red"))

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
            angle_rad = radians(angle_deg)
            x = self.center_x + self.hex_size * cos(angle_rad)
            y = self.center_y + self.hex_size * sin(angle_rad)
            points.append(QPointF(x, y))
        return QPolygonF(points)

    def __len__(self):
        return len(self._core)

    def __getitem__(self, index):
        return self._core[index]

    def __setitem__(self, key, value):
        self._core[key] = value

    def __delitem__(self, index):
        del self._core[index]

    def style_hex(self):
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)

    def create_arrow___(self, vector_dir=None):
        if (self.i, self.j) in [(3, 4), (4, 4)]:
            self.vector_dir = math.radians(120)
            vector_dir = math.radians(120)
        if not vector_dir:
            vector_dir = self.vector_dir
        if not self.show_arrows or vector_dir is None:
            self._arrow = []
            self._content = [self, ] + self._arrow
            return None
        vec_x_end = self.center_x + self.vector_length * cos(vector_dir)
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

    def create_arrow(self, vector_dir=None):
        if not vector_dir:
            vector_dir = self.vector_dir
        if not self.show_arrows or vector_dir is None:
            self._arrow = []
            self._content = [self, ] + self._arrow
            return None

        if radians(0) < vector_dir < radians(270):
            sin_multiplier = 1
        else:
            sin_multiplier = 1

        vec_x_end = self.center_x + self.vector_length * math.cos(vector_dir)
        vec_y_end = self.center_y + self.vector_length * math.sin(
            vector_dir) * sin_multiplier  # TODO: fix y axis parity

        line = QGraphicsLineItem(self.center_x, self.center_y, vec_x_end, vec_y_end)
        # Calculate arrow angles
        arrow_angle1 = vector_dir + math.radians(135)
        arrow_angle2 = vector_dir - math.radians(135)

        arrow_length = self.vector_length / 2

        arrow_right = QGraphicsLineItem(
            vec_x_end, vec_y_end,
            vec_x_end + arrow_length * math.cos(arrow_angle1),
            vec_y_end + arrow_length * math.sin(arrow_angle1) * sin_multiplier
        )

        arrow_left = QGraphicsLineItem(
            vec_x_end, vec_y_end,
            vec_x_end + arrow_length * math.cos(arrow_angle2),
            vec_y_end + arrow_length * math.sin(arrow_angle2) * sin_multiplier
        )

        line.setPen(self.vector_pen)
        arrow_left.setPen(self.vector_pen)
        arrow_right.setPen(self.vector_pen)

        self._arrow = [line, arrow_left, arrow_right]
        self._content = [self, ] + self._arrow


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

    def turn_on_off(self, state):
        if state:
            self.setPen(self.ON_pen)
            #self.setBrush(self.ON_brush)
        else:
            self.setPen(self.OFF_pen)
            #self.setBrush(self.OFF_brush)

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


class Lane(QGraphicsRectItem):
    def __init__(self, x, y, width, height, show_arrow, orientation, parent, input_dir, i, j, *args):
        super().__init__(x, y, width, height, *args)
        self._arrow = None
        self.i = i
        self.j = j
        self.input_dir = input_dir
        self.parent = parent
        self._content = []
        self.show_arrows = show_arrow
        self.vector_length = max(height, width) * 0.8
        self.x = x
        self.y = y
        self.center_x = 0
        self.center_y = 0
        self.orientation = orientation

        self._start_highlight = 0
        self._end_highlight = 0
        self._obstacle_highlight = 0

        self.default_brush = QBrush(QColor("Blue"))
        self.default_pen = QPen(QColor("White"))

        self.obstacle_brush = QBrush(QColor("grey"))
        self.obstacle_pen = QPen(QColor("white"))

        self.start_brush = QBrush(QColor("light green"))
        self.start_pen = QPen(QColor("while"))

        self.end_brush = QBrush(QColor("red"))
        self.end_pen = QPen(QColor("orange"))

        self.setBrush(self.default_brush)
        self.setPen(self.default_pen)

        self.vector_pen = QPen(QColor("red"))
        # create arrow
        vector_dir = 0
        arrow_back = max(height, width)
        arrow_offset = min(height, width)

        if orientation[0] == 0:
            if orientation[1] == 1:  # left
                if self.input_dir == 'Input':
                    vector_dir = 0
                    self.center_x = self.x + arrow_back * 0.1
                    self.center_y = self.y + arrow_offset / 2
                else:
                    vector_dir = math.pi
                    self.center_x = self.x + arrow_back * 0.9
                    self.center_y = self.y + arrow_offset / 2
            else:  # right
                if self.input_dir == 'Input':
                    vector_dir = math.pi if self.input_dir == 'Input' else 0
                    self.center_x = self.x + arrow_back * 0.9
                    self.center_y = self.y + arrow_offset / 2
                else:
                    vector_dir = 0
                    self.center_x = self.x + arrow_back * 0.1
                    self.center_y = self.y + arrow_offset / 2
        elif orientation[1] == 0:
            if orientation[0] == 1:  # bottom
                if self.input_dir == 'Input':
                    vector_dir = 4.71239
                    self.center_x = self.x + arrow_offset / 2
                    self.center_y = self.y + arrow_back * 0.9
                else:
                    vector_dir = math.pi / 2
                    self.center_x = self.x + arrow_offset / 2
                    self.center_y = self.y + arrow_back * 0.1
            else:  # top
                if self.input_dir == 'Input':
                    vector_dir = math.pi / 2
                    self.center_x = self.x + arrow_offset / 2
                    self.center_y = self.y + arrow_back * 0.1
                else:
                    vector_dir = 4.71239
                    self.center_x = self.x + arrow_offset / 2
                    self.center_y = self.y + arrow_back * 0.9
        self.create_arrow(vector_dir=vector_dir)

    def create_arrow(self, vector_dir=None):

        if not self.show_arrows or vector_dir is None:
            self._arrow = []
            self._content = [self, ] + self._arrow
            return None
        vec_x_end = self.center_x + self.vector_length * cos(vector_dir)
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

    def get_lane_data(self):
        return {'cell_index': [self.x, self.y], 'orientation': self.orientation, 'input_dir': self.input_dir}

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if value in self._content:
            self._content.remove(value)
        else:
            self._content.append(value)

    def highlight(self, highlight_type: str):
        if highlight_type == 'start':
            if self._start_highlight == 1:
                self._start_highlight = 0
                self.setBrush(self.default_brush)
                self.setPen(self.default_pen)
            else:
                self._start_highlight = 1
                self.setBrush(self.start_brush)
                self.setPen(self.start_pen)
        elif highlight_type == 'end':
            if self._end_highlight == 1:
                self._end_highlight = 0
                self.setBrush(self.default_brush)
                self.setPen(self.default_pen)
            else:
                self._end_highlight = 1
                self.setBrush(self.end_brush)
                self.setPen(self.end_pen)
        elif highlight_type == 'obstacle':
            if self._obstacle_highlight == 1:
                self._obstacle_highlight = 0
                self.setBrush(self.default_brush)
                self.setPen(self.obstacle_pen)
            else:
                self._obstacle_highlight = 1
                self.setBrush(self.obstacle_brush)
                self.setPen(self.obstacle_pen)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.i == other.i and self.j == other.j
        elif isinstance(other, list | tuple):
            return self.i == other[0] and self.j == other[1]
        else:
            return False


class BackgroundItem(QGraphicsItemGroup):  # QGraphicsPolygonItem
    hex_size = 40
    lane_width = hex_size * 1.3
    lane_height = hex_size * 2.5
    y_spacing = hex_size * 1.5
    x_spacing = hex_size * 1.73
    vector_length = hex_size / 2

    def __init__(self, scene, rows, cols, show_arrows, path=None, angle_field=None):
        super().__init__()
        # 0, 0, cols * cell_width, rows * cell_height
        self.scene = scene
        self.angle_field = angle_field
        self.path = path

        # Size of hexagons

        self.rows = rows
        self.cols = cols
        self.initial_pos_x = self.rows * self.hex_size * 0.5
        self.initial_pos_y = self.cols * self.hex_size * 0.5

        self._positions = []
        self._hexs_: list[list[Hexagon]] = []
        self._obstacle: list[list[int]] = []
        self._selected: list[list[int]] = []
        self._vector_field: list[list[list[float]]] = []
        self._lane_list = []
        self._content = []
        self._add_to_vector_field = True
        self.list_with_dif_color = []
        self.last_unit_vector = None

        # create_stuff
        for i in range(self.rows):
            self._positions.append([])
            for j in range(self.cols):
                center_y = self.initial_pos_x + self.y_spacing * i  # + (self.hex_size * 0.9 if j % 2 == 0 else 0)
                center_x = self.initial_pos_y + self.x_spacing * j + (self.hex_size * 0.9 if i % 2 == 0 else 0)
                self._positions[i].append([center_x, center_y])

        self.vector_pen = QPen(QColor("yellow"))
        self.vector_brush = QBrush(QColor('blue'))
        self.vector_dir = None

        self.pen = QPen(QColor("green"))
        self.brush = QBrush(QColor('blue'))
        self.show_arrows = show_arrows
        self.create_table()  # TODO: replace x and  with table position

    def create_hexagon(self, center_x, center_y):
        points = []
        for i in range(6):
            angle_deg = 60 * i + 30
            angle_rad = radians(angle_deg)
            x = center_x + self.hex_size * cos(angle_rad)
            y = center_y + self.hex_size * sin(angle_rad)
            points.append(QPointF(x, y))
        return QPolygonF(points)

    @property
    def positions(self):
        return self._positions

    @property
    def hexs(self) -> list[list[Hexagon]]:
        return self._hexs_

    @hexs.setter
    def hexs(self, value):
        # TODO: Need better way to update it
        for line in range(len(self.hexs)):
            for cell in range(len(self.hexs[line])):
                self.hexs[line][cell].obstacle = 1 if value[line][cell] else 0

    @property
    def obstacle(self):
        self._obstacle = []
        for line in range(self.rows):  # range(len(self.hexs)):
            self._obstacle.append([])
            for cell in range(self.cols):  # range(len(self.hexs[line])):
                if self.hexs[line][cell].obstacle:
                    self._obstacle[line].append(1)
                else:
                    self._obstacle[line].append(0)
        return self._obstacle

    def clear_all_highlight(self):
        for line in range(len(self.hexs)):
            for cell in range(len(self.hexs[line])):
                self.hexs[line][cell].highlight = 0
                self.hexs[line][cell].selected = 0

    def highlight_list(self, points, off=False):
        for point in points[1:len(points) - 1]:
            self.hexs[point[0]][point[1]].selected = 1 if not off else 0

    @obstacle.setter
    def obstacle(self, value: list[list[int]]):
        for line in range(len(self.hexs)):
            for cell in range(len(self.hexs[line])):
                self._obstacle[line][cell] = value[line][cell]

    @property
    def vector_field(self):
        return self._vector_field

    @vector_field.setter
    def vector_field(self, val):
        self._vector_field = val

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    def highlight_point(self, cor, flip=True, obstacle=False, s_e='start'):
        """Flips highlight"""
        if isinstance(cor, dict):
            t = 0
            for line in range(len(self.hexs)):
                for cell in range(len(self.hexs[line])):
                    if (cell, line) == cor['start']:
                        t += 1
                        self.hexs[cell][line].specific_highlight('start')
                    elif (cell, line) == cor['end']:
                        t += 1
                        self.hexs[cell][line].specific_highlight('end')
                    elif 'obstacle' in cor.keys() and (cell, line) in cor['obstacle']:
                        t += 1
                        self.hexs[cell][line].obstacle = 1
        if isinstance(cor, tuple | list):
            if obstacle:
                t = self.hexs[cor[0]][cor[1]].obstacle
                self.hexs[cor[0]][cor[1]].obstacle = not t if flip else t
            else:
                self.hexs[cor[0]][cor[1]].specific_highlight(s_e)

    def create_table(self):
        drawing_path, current_index, future_index = False, 0, 1
        if self.path or self.list_with_dif_color:
            drawing_path = True
            logger.info("Drawing path")
        self._hexs_ = []
        self._vector_field = []
        logger.info(f"creating table")
        for i in range(self.rows):
            self._hexs_.append([])
            self._vector_field.append([])
            for j in range(self.cols):
                show_arrows = self.show_arrows
                # Displaying the vector
                if drawing_path:
                    if (i, j) in self.path:
                        current_index = self.path.index((i, j))
                        t = 0
                        if current_index == len(self.path) - 1:
                            for lane in self.lane_list:
                                if lane.i == i and lane.j == j:
                                    x_end, y_end = self.path[current_index]
                                    x_start, y_start = i, j

                                    x_end, y_end = self.positions[x_start][y_start]
                                    x_start, y_start = lane.position

                                    t = [x_start - x_end, (y_start - y_end)]
                                    # TODO: You keep tackling runtime mistakes here
                                    magnitude = np.linalg.norm(t)
                                    if magnitude == 0:
                                        raise ValueError("Cannot normalize the zero vector")
                                    unit_vector = t / magnitude
                                    angle_rad = math.atan2(unit_vector[1], unit_vector[0])
                                    self.vector_dir = angle_rad
                        else:

                            x_end, y_end = self.path[current_index]
                            x_start, y_start = self.path[current_index + 1]

                            x_end, y_end = self.positions[x_end][y_end]
                            x_start, y_start = self.positions[x_start][y_start]

                            t = [x_start - x_end, (y_start - y_end)]
                            magnitude = np.linalg.norm(t)
                            if magnitude == 0:
                                raise ValueError("Cannot normalize the zero vector")
                            unit_vector = t / magnitude
                            angle_rad = math.atan2(unit_vector[1], unit_vector[0])
                            self.vector_dir = angle_rad
                    else:
                        show_arrows = False
                        self.vector_dir = None
                    if (i, j) in self.list_with_dif_color and len(self.list_with_dif_color) >= 2: # TODO: Here is the mask cells
                        try:
                            x_end, y_end = self.path[0]
                            x_start, y_start = self.path[1]

                            x_end, y_end = self.positions[x_end][y_end]
                            x_start, y_start = self.positions[x_start][y_start]

                            t = [x_start - x_end, y_start - y_end]
                            magnitude = np.linalg.norm(t)
                            if magnitude == 0:
                                raise ValueError("Cannot normalize the zero vector")
                            unit_vector = t / magnitude
                            self.last_unit_vector = unit_vector
                        except:
                            assert self.last_unit_vector is not None, 'No unit vector history'
                            unit_vector = self.last_unit_vector
                        angle_rad = math.atan2(unit_vector[1], unit_vector[0])
                        self.vector_dir = angle_rad
                        show_arrows = True
                        logger.info(f'cell: {(i, j)} normalized: {unit_vector}, angle_rad: {angle_rad}')
                elif self.angle_field is not None:
                    t = self.angle_field[i][j]
                    if t[0] is None:
                        self.vector_dir = None
                    else:
                        # angle_rad = math.atan2(t[1], t[0])
                        angle_rad = math.atan2(t[1], t[0])
                        self.vector_dir = angle_rad
                if (i, j) in self.list_with_dif_color:
                    self.arrow_color = 'red'
                else:
                    self.arrow_color = 'yellow'
                if self.vector_dir:

                    hexagon = Hexagon(self.positions[i][j][0], self.positions[i][j][1], vector_dir=self.vector_dir,
                                      show_arrows=show_arrows, i=i, j=j, arrow_color=self.arrow_color)
                    if self._add_to_vector_field:
                        self._vector_field[i].append([cos(self.vector_dir), sin(self.vector_dir), 0])
                    else:
                        self._vector_field[i].append([0, 0, 0])
                    self._hexs_[i].append(hexagon)
                else:
                    hexagon = Hexagon(self.positions[i][j][0], self.positions[i][j][1], vector_dir=None,
                                      show_arrows=show_arrows, i=i, j=j, arrow_color=self.arrow_color)
                    self._vector_field[i].append([0, 0, 0])
                    self._hexs_[i].append(hexagon)

        self.path = []
        self.add_items_to_group()

    def modify_lanes(self, add: bool, edge_cell_index: list, position: list, direction: str):
        if add:
            orientation, _ = self.get_direction_to_table(edge_cell_index[0], edge_cell_index[1], rows=self.rows,
                                                         cols=self.cols)
            cell_to_connect_center = self.positions[edge_cell_index[0]][edge_cell_index[1]]

            # x = self.hex_size * 0 * orientation[0] + self.positions[edge_cell_index[0]][edge_cell_index[1]][0] - self.hex_size * 0.5
            # y = self.lane_height * orientation[1] + self.positions[edge_cell_index[0]][edge_cell_index[1]][1]
            data_to_create_rep = [edge_cell_index[0], edge_cell_index[1], direction]
            x, y = [0, 0]
            logger.critical(f'Adding lane to {orientation}')
            if orientation[0] == 0:
                if orientation[1] == 1: # left
                    x = self.positions[edge_cell_index[0]][edge_cell_index[1]][0] - self.lane_height - self.hex_size * 0.9
                    y = self.positions[edge_cell_index[0]][edge_cell_index[1]][1] - self.lane_width * 0.5
                else: # right
                    x = self.positions[edge_cell_index[0]][edge_cell_index[1]][0] + self.lane_height * 0.36
                    y = self.positions[edge_cell_index[0]][edge_cell_index[1]][1] - self.lane_width * 0.5
                rect = Lane(x, y, self.lane_height, self.lane_width, show_arrow=self.show_arrows,
                            orientation=orientation, parent=self, input_dir=direction, i=edge_cell_index[0],
                            j=edge_cell_index[1])
                self._content.append(
                    [x, y, self.lane_height, self.lane_width, self.show_arrows, orientation, self, direction,
                     edge_cell_index[0], edge_cell_index[1]])
            else:
                if orientation[0] == -1: # top
                    x = self.positions[edge_cell_index[0]][edge_cell_index[1]][0] - self.lane_width * 0.5
                    y = self.positions[edge_cell_index[0]][edge_cell_index[1]][
                            1] - self.lane_height - self.hex_size * 0.9
                else: # bottom
                    x = self.positions[edge_cell_index[0]][edge_cell_index[1]][0] - self.lane_width * 0.5
                    y = self.positions[edge_cell_index[0]][edge_cell_index[1]][1] + self.hex_size * 0.9
                rect = Lane(x, y, self.lane_width, self.lane_height, show_arrow=self.show_arrows,
                            orientation=orientation, parent=self, input_dir=direction, i=edge_cell_index[0],
                            j=edge_cell_index[1])
                self._content.append(
                    [x, y, self.lane_width, self.lane_height, self.show_arrows, orientation, self, direction,
                     edge_cell_index[0], edge_cell_index[1]])

            for c in rect.content:
                self._lane_list.append(c)
                self.addToGroup(c)
            data_to_create_rep.append([x, y])
            return data_to_create_rep

    @staticmethod
    def get_direction_to_table(cell_x, cell_y, rows, cols):
        """
        This function determines the direction (unit vector or angle) a cell outside the table needs to point to reach the edge of the table.

        Args:
            cell_x: X-coordinate of the cell outside the table.
            cell_y: Y-coordinate of the cell outside the table.
            rows: Number of rows in the table.
            cols: Number of columns in the table.

        Returns:
            A tuple containing:
                - A unit vector pointing towards the table (x, y).
                - An angle in radians (0, pi/2, pi, pi*3/2, or 2*pi) representing the direction.
        """

        # Table-top left and bottom right corner coordinates
        top_left_x, top_left_y = 0, 0
        bottom_right_x, bottom_right_y = cols - 1, rows - 1

        # Calculate direction based on cell position relative to table edges
        direction_x = 0
        direction_y = 0
        if cell_x == top_left_x:
            direction_x = -1  # Right towards table
        elif cell_x == bottom_right_x:
            direction_x = 1  # Left towards table
        if cell_y == top_left_y:
            direction_y = 1  # Up towards table
        elif cell_y == bottom_right_y:
            direction_y = -1  # Down towards table

        # Adjust direction for corner cases
        if direction_x == 0 and (cell_y < top_left_y or cell_y > bottom_right_y):
            direction_y = 0  # No vertical movement for cells on edges without vertical movement

        if direction_y == 0 and (cell_x < top_left_x or cell_x > bottom_right_x):
            direction_x = 0  # No horizontal movement for cells on edges without horizontal movement

        # Calculate unit vector and angle based on combined direction
        if direction_x == 0:
            unit_vector = (0, direction_y)
            if direction_y > 0:
                angle = math.pi / 2
            else:
                angle = 3 * math.pi / 2
        else:
            unit_vector = (direction_x, 0)
            if direction_x > 0:
                angle = 0
            else:
                angle = math.pi

        return unit_vector, angle

    def add_items_to_group(self, group=None):
        if group is None:
            self._content = []
            for line in range(len(self.hexs)):
                for cell in range(len(self.hexs[line])):
                    for item in self.hexs[line][cell].content:
                        self.addToGroup(item)
            for lane in self._lane_list:
                self.addToGroup(lane)
        else:
            for item in group:
                logger.info("Adding lanes from past stuff")
                try:
                    it = Lane(item[0], item[1], item[2], item[3], show_arrow=self.show_arrows, orientation=item[5],
                              parent=item[6], input_dir=item[7], i=item[8], j=item[9])
                    for c in it.content:
                        self.addToGroup(c)
                except:
                    logger.info("one hex deleted")

    def draw_path_arrows(self, cell_list: list[list[int, int]], lane_list, do_not_include_in_field:bool,
                         list_with_dif_color:list|None=None, arrow_color:str='yellow', dir_vec=None):
        self.path = cell_list #+ list_with_dif_color
        self.list_with_dif_color = list_with_dif_color
        self.directional_vector = dir_vec
        self.lane_list = lane_list
        self.arrow_color = arrow_color
        if do_not_include_in_field:
            self._add_to_vector_field = False
        self.create_table()
        if do_not_include_in_field:
            self._add_to_vector_field = True

class Table_preview(QWidget):
    json_vec_field_filename = r'C:\Users\toupa\Desktop\ESE - S1\PFE\3D\New folder\controllers\dataexchange.pkl'

    def __init__(self, *args):
        super().__init__(*args)
        self.show_ghost_simulation = True
        self.select_start = None
        self.select_end = None
        self.select_obstacle = None
        self._shared_data = {}
        self._initial_info = {}
        self._foldable_toolbar: FoldableToolBar | None = None
        self.drag_rectangle = None
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._package_size = 20
        self.show_arrows = False
        self.angle_field = None
        self._package_size = 60
        self._lane_representation_list = []
        self._last_recorded_velocity_vector_field = None
        self._last_recorded_velocity_count = 10

        # hover constants
        self.hover_with_mouse = False

        self._main: None|QMainWindow = None
        self.parent = self.parent()
        self.parent.objectName()
        self.background_item = None
        self.view = QGraphicsView()
        self.view.setMouseTracking(True)
        self.scene = QGraphicsScene()
        self.paths = [[], ]
        self.coor_list = []

        self.path_index = 0
        self.coor_index = 0

        # Set up scenes
        self.table_cols = 2
        self.table_rows = 2
        self.setup_background_scene()

        # TODO: get row_count and _y from MainUi and save then as self.cols etc then run the entire update to the preview
        # self.update_button.clicked.connect(self.update_background_scene)
        objname = self.objectName()
        self.add_lanes = self.parent.findChild(QPushButton, 'add_lanes')
        self.remove_lanes = self.parent.findChild(QPushButton, 'remove_lanes')
        self.add_lanes_in_out = self.parent.findChild(QComboBox, 'add_lanes_in_out')
        try:
            self.add_lanes.clicked.connect(self.send_lane_rep_list)
        except Exception as e:
            logger.info(f"can't connect the send rep list method because of: {e}")
        self.setup_buttons()
        # Variables to track drawing
        self.last_point = None
        self.drawing = False

    def set_main(self, main: QMainWindow):
        self._main = main

    def setup_ghost(self):
        # ghost rect ooooooooooooooooooooo
        self.ghost_rect = QGraphicsRectItem(0, 0, 100, 200)
        translucent_grey = QColor(128, 128, 128, 128)  # RGBA: Grey color with 50% opacity
        self.ghost_rect.setBrush(QBrush(translucent_grey))  # TODO: Check #1
        self.ghost_item = self.scene.addItem(self.ghost_rect)
        self.ghost_rect.hide()

    def send_lane_rep_list(self):
        self.foldable_toolbar._lane_representation_list = self._lane_representation_list

    @staticmethod
    def closest_position(positions, target):
        """
        Find the closest position to the target from a list of positions.

        :param positions: List of tuples representing positions (e.g., [(x1, y1), (x2, y2), ...])
        :param target: Tuple representing the target coordinate (e.g., (x, y))
        :return: Tuple representing the closest position to the target
        """
        if not positions:
            return None

        closest_pos = positions[0]
        max_distance = Table_preview.euclidean_distance(closest_pos, target)

        for pos in positions[1:]:
            distance = Table_preview.euclidean_distance(pos, target)
            if distance > max_distance:
                closest_pos = pos
                max_distance = distance

        return closest_pos

    @staticmethod
    def euclidean_distance(p1, p2):
        """
        Calculate the Euclidean distance between two points.

        :param p1: Tuple representing the first point (x1, y1)
        :param p2: Tuple representing the second point (x2, y2)
        :return: Euclidean distance between the points
        """
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    @staticmethod
    def is_inside_hex(polygons: list[QPolygonF], rect: QRectF) -> list[tuple[int, int]]:
        ans = []  # list of polygons inside the rect
        for i in range(len(polygons)):
            for j in range(len(polygons[i])):
                poly = polygons[i][j]
                for point_indx in range(len(poly)):
                    if rect.contains(poly[point_indx]) and (i, j) not in ans:
                        ans.append((i, j))
        return ans

    def update_package_location(self):
        # TODO: Use QTimer, maybe 200ms? More, focus on performance, sim is too slow anyways.
        # TODO: create supervisor to place objects as well as know when simulation is finished, need info dict in shrm

        """Runs periodically using QTimer.
            Extracts sensor data from shared memory and updates hexagon highlight state.
            Will be first launched after self.launched_button is triggered.
            """
        logger.info('Updating')
        logger.info(f'queue: {self.foldable_toolbar.package_queue}')
        logger.info(f'lanes: {self.foldable_toolbar.lane_representation_list}')
        self._shared_data = shared_mem.retrieve_data()
        t = self._shared_data[SharedData.sensor_field]

        self.background_item.hexs = t
        grid = self.background_item.obstacle
        logger.debug(f'grid before: {grid}')
        cells_with_packages_on_them = []
        centers_of_cells_with_packages_on_them = []
        for i in range(self.table_rows):
            for j in range(self.table_cols):
                if t[i][j]:
                    grid[i][j] = 0
                    cells_with_packages_on_them.append((i, j))
                    centers_of_cells_with_packages_on_them.append(self.background_item.positions[i][j])
        logger.debug(f'grid after: {grid}')

        if centers_of_cells_with_packages_on_them:
            logger.info(f'The packages are on cells: {cells_with_packages_on_them}')
            ghost_package_x = sum([i[0] for i in centers_of_cells_with_packages_on_them]) / len(
                centers_of_cells_with_packages_on_them)
            ghost_package_y = sum([i[1] for i in centers_of_cells_with_packages_on_them]) / len(
                centers_of_cells_with_packages_on_them)
            logger.info(f'the ghost packages has coordinates: {[ghost_package_x, ghost_package_y]}')
            # TODO: get pacakge size to here

            if self.show_ghost_simulation and self.objectName() == 'table_draw_enabled':
                self.ghost_rect.show()
                self.ghost_rect.setRect(ghost_package_x - 50, ghost_package_y - 50, 100, 100)
            elif self.objectName() == 'table_draw_enabled' and not self.show_ghost_simulation:
                self.ghost_rect.hide()


            d = self.initial_info
            # TODO: Make it smarter
            end = d['end']
            cloest_cor = self.closest_position(positions=centers_of_cells_with_packages_on_them, target=end)
            d['start'] = cells_with_packages_on_them[centers_of_cells_with_packages_on_them.index(cloest_cor)]
            start = tuple(d['start'])
            try:
                obstacles = d['obstacle']
            except Exception:
                obstacles = []
            # Get the surrounding hexs, and only turn them ON, rest are OFF, not matter what
            cells_online = self.is_inside_hex(self.background_item.hexs, self.ghost_rect.rect())
            # TODO: Here are online cells
            for p in obstacles:
                grid[p[0]][p[1]] = 1

            self.cell_grid = CelluvoyerGrid(grid)
            paths = CelluvoyerGrid.a_star_search(self.cell_grid, start, end, max_paths=2)
            if not paths:
                self.foldable_toolbar.current_angle.setText("NO PATH FOUND")
                return
            #self.background_item.highlight_list(paths[0])

            vector_field = self.background_item.vector_field
            if len(paths) != 0 and len(paths[0]) >= 2:
                x_end, y_end = paths[0][0]
                x_start, y_start = paths[0][1]

                x_end, y_end = self.background_item.positions[x_end][y_end]
                x_start, y_start = self.background_item.positions[x_start][y_start]

                self.directional_vector = [1*(y_start - y_end), x_start - x_end, 0]
                magnitude = np.linalg.norm(self.directional_vector)
                if magnitude == 0:
                    raise ValueError("Cannot normalize the zero vector")
                unit_vector = self.directional_vector / magnitude
                self.directional_vector = unit_vector

            angle_rad = math.atan2(self.directional_vector[1], self.directional_vector[0])
            # ----------------------------------------------------------------
            r = 0.04  # Distance from center to wheel (example value)

            # Transformation matrix
            T2 = np.array([
                [0, 1, r],
                [-np.sqrt(3) / 2, -0.5, r],
                [np.sqrt(3) / 2, -0.5, r]
            ])
            T = np.array([
                [-np.sin(np.pi / 6), np.cos(np.pi / 6), r],
                [-np.sin(5 * np.pi / 6), np.cos(5 * np.pi / 6), r],
                [-np.sin(3 * np.pi / 2), np.cos(3 * np.pi / 2), r]
            ])
            # Velocity vector
            V = np.array(self.directional_vector)

            # Calculate wheel speeds
            wheel_speeds = np.dot(T, V)
            # ----------------------------------------------------------------
            to_print = [round(i, 1) for i in wheel_speeds]
            self.foldable_toolbar.current_angle.setText(f"Angle: {round(math.degrees(angle_rad), 2)}\nengines: {to_print}")
            angle_rad = math.atan2(self.directional_vector[1], self.directional_vector[0])
            logger.info(f'The total group direction is: {math.degrees(angle_rad)}')
            for on_cell_coordinates in cells_online:
                vector_field[on_cell_coordinates[0]][on_cell_coordinates[1]] = self.directional_vector
            if not self._main.actionShow_ON_vectors.isChecked():
                cells_online_arg = []
            else:
                cells_online_arg = cells_online
            self.background_item.draw_path_arrows(paths[0], lane_list=self.lane_representation_list,
                                                  do_not_include_in_field=True, list_with_dif_color=cells_online_arg, dir_vec=self.directional_vector)  # This will only draw commands, not send them to vec field
            self.background_item.highlight_point(self.initial_info)
            if self._main.actionShow_ON_OFF.isChecked():
                for i in range(len(self.background_item.hexs)):
                    for j in range(len(self.background_item.hexs[i])):
                        if (i, j) in cells_online:
                            self.background_item.hexs[i][j].turn_on_off(True)
                        else:
                            self.background_item.hexs[i][j].turn_on_off(False)
            self._last_recorded_velocity_vector_field = vector_field
            d = shared_mem.retrieve_data()
            d[SharedData.vector_field] = vector_field
            d[SharedData.simulation_information]['rows'] = len(grid)
            d[SharedData.simulation_information]['cols'] = len(grid[0])
            shared_mem.store_data(d)
        elif self._last_recorded_velocity_vector_field and self._last_recorded_velocity_count:
            self._last_recorded_velocity_count -= 1
            d = shared_mem.retrieve_data()
            d[SharedData.vector_field] = self._last_recorded_velocity_vector_field
            d[SharedData.simulation_information]['rows'] = len(grid)
            d[SharedData.simulation_information]['cols'] = len(grid[0])
            shared_mem.store_data(d)
        '''try:
            self._shared_data = shared_mem.retrieve_data()
            self.background_item: BackgroundItem
            self.background_item.hexs = self._shared_data[SharedData.sensor_field]
        except Exception as e:
            logger.info(f"Simulation is offline because: {e}. We're inside: {self.objectName()}, instance:{self}")
        '''

    def setup_buttons(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout_button = QHBoxLayout()
        button_widget = QWidget()
        button_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.clear_drawing = QPushButton('Clear')
        self.calculate = QPushButton('Calculate')
        self.launch = QPushButton('Launch')

        self.calculate.setObjectName('calculate_button')
        self.launch.setObjectName('launch_button')
        self.launch.setCheckable(True)
        self.launch.setChecked(False)

        self.clear_drawing.clicked.connect(self.update_foreground_scene)
        self.calculate.clicked.connect(self.calculate_path)

        layout_button.addWidget(self.clear_drawing)
        layout_button.addWidget(self.calculate)
        layout_button.addWidget(self.launch)
        button_widget.setLayout(layout_button)
        if self.parent.objectName() == 'preview_mode':
            pass  # do not any but the preview, no drawing, too.
        elif self.parent.objectName() == 'edit_mode':
            self.view.viewport().installEventFilter(self)
            layout.addWidget(button_widget)
        self.setLayout(layout)

    def setup_auto_button(self, start, end, obstacle):
        self.select_start: QPushButton = start
        self.select_end: QPushButton = end
        self.select_obstacle: QPushButton = obstacle

        '''self.select_start.clicked.connect(self.highlight_after_depress)
        self.select_end.clicked.connect(self.highlight_after_depress)
        self.select_obstacle.clicked.connect(self.highlight_after_depress)'''

    def highlight_after_depress(self):
        # TODO: must unhighlight right after, not before. Fix this. Example, if you highlight two cells then
        #  unhighlight one, the unhighlighted one will be selected while appearing not to
        if self.select_start.isChecked():
            self.background_item.highlight_point(self.initial_info['start'], True, obstacle=False, s_e='start')
        elif self.select_end.isChecked():
            self.background_item.highlight_point(self.initial_info['end'], True, obstacle=False, s_e='end')
        elif self.select_obstacle.isChecked():
            p = self.initial_info['obstacle'][-1]
            l = len(self.initial_info['obstacle'])
            if p in self.initial_info['obstacle'][:l - 1]:
                self._initial_info['obstacle'].remove(p)
                self._initial_info['obstacle'].remove(p)
            self.background_item.highlight_point(p, True, obstacle=True)

    def numpy_array_to_list(self, arr):
        if isinstance(arr, np.ndarray):
            return arr.tolist()  # If arr is a NumPy array, convert it to a list recursively
        elif isinstance(arr, (list, tuple)):
            return [self.numpy_array_to_list(item) for item in
                    arr]  # Recursively process each element if arr is a list or tuple
        else:
            return arr

    def calculate_path(self):
        pen = QPen(Qt.red, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        for p in self.paths[self.path_index - 1]:
            self.scene.addPath(p,
                               pen)  # self.angle_field = self.get_vec_field_from_path(0)   # TODO: add list to choose from in QAction menu
        points = self.coor_list[self.coor_index - 1]
        vec_fiel = self.background_item.positions
        # TODO: Add threshold to gui
        self.angle_field = self.create_vector_field(points, vec_fiel, self.table_rows, self.table_cols)
        self._shared_data[SharedData.vector_field] = self.angle_field
        if SharedData.simulation_information not in self._shared_data.keys():
            self._shared_data[SharedData.simulation_information] = {'rows': self.table_rows, 'cols': self.table_cols}
        else:
            self._shared_data[SharedData.simulation_information]['rows'] = self.table_rows
            self._shared_data[SharedData.simulation_information]['cols'] = self.table_cols

        shared_mem.store_data(self._shared_data)

        self.update_background_scene()  # TODO: Create option not to delete rects + lines
        # self.scene.addItem(self.background_item)
        # self.view.setScene(self.scene)

    def create_vector_field(self, path_points, vec_fiel, x, y):
        vector_field = [[0 for j in range(y)] for i in range(x)]
        for i in range(len(vec_fiel)):
            for j in range(len(vec_fiel[i])):
                cell = vec_fiel[i][j]  # TODO: If grids topped working, here
                vector_field[i][j] = self.get_distance_and_tangent(cell, path_points, self._package_size)

        return vector_field

    def get_distance_and_tangent(self, cell_center, waypoints, threshold):
        """
        Calculates the distance and tangent vector from a cell center to the closest point on a line segment.

        Args:
            cell_center: A list representing the coordinates of the cell center (x, y).
            waypoints: A list of lists representing the waypoints defining the line segment (start and end points).
            threshold: The maximum distance for considering a cell close to the line segment.

        Returns:
            A tuple containing:
                - distance: The distance between the cell center and the closest point on the line segment (or None if exceeding threshold).
                - tangent: The tangent vector of the line segment (or None if exceeding threshold).
        """

        min_distance = np.inf
        closest_tangent = None
        for i in range(len(waypoints) - 1):
            current_point = waypoints[i]
            next_point = waypoints[i + 1]

            tangent = np.array(next_point) - np.array(current_point)

            distance, projection = self.get_distance_to_line_segment(cell_center, current_point, next_point)

            # Update minimum distance and tangent if closer than previous ones
            if distance is not None and distance < min_distance:
                min_distance = distance
                closest_tangent = tangent

        if min_distance <= threshold:
            # normalize
            magnitude = np.linalg.norm(closest_tangent)  # Calculate the magnitude of the vector
            return list(closest_tangent / magnitude) + [0, ]
        else:
            return [None, None, None]

    @staticmethod
    def get_distance_to_line_segment(cell_center, start_point, end_point):
        """
        Helper function to calculate distance between a point and a line segment.
        (This function can be replaced with your preferred distance calculation method)
        """

        # Same logic as before for distance calculation (refer to previous explanation)
        line_direction = np.array(end_point) - np.array(start_point)
        cell_to_start = np.array(cell_center) - np.array(start_point)
        t = np.dot(cell_to_start, line_direction) / np.dot(line_direction, line_direction)
        t = np.clip(t, 0, 1)
        projection = start_point + t * line_direction
        distance = np.linalg.norm(cell_center - projection)
        return distance, projection

    def setup_background_scene(self, items_from_other_instance=None):
        # self.background_item.clear_all_highlight()
        logger.info(f"Background scene is updated ----------------------------------------------------------------")
        items = []
        if items_from_other_instance is not None:
            items = items_from_other_instance
        elif self.background_item is not None:
            items = self.background_item.content
        self.scene.clear()
        # self.angle_field = [[[1.0, 0.0, 0], [0.9685831611286311, 0.2486898871648548, 0], [0.8763066800438636, 0.4817536741017153, 0], [0.7289686274214116, 0.6845471059286887, 0], [0.5358267949789965, 0.8443279255020151, 0]], [[0.30901699437494745, 0.9510565162951535, 0], [0.0627905195293133, 0.9980267284282716, 0], [-0.1873813145857246, 0.9822872507286887, 0], [-0.4257792915650727, 0.9048270524660195, 0], [-0.6374239897486897, 0.7705132427757893, 0]], [[-0.8090169943749473, 0.5877852522924732, 0], [-0.9297764858882515, 0.36812455268467775, 0], [-0.9921147013144779, 0.1253332335643041, 0], [-0.9921147013144779, -0.12533323356430429, 0], [-0.9297764858882515, -0.3681245526846779, 0]], [[-0.8090169943749475, -0.587785252292473, 0], [-0.6374239897486895, -0.7705132427757894, 0], [-0.42577929156507216, -0.9048270524660198, 0], [-0.18738131458572463, -0.9822872507286887, 0], [0.06279051952931372, -0.9980267284282716, 0]], [[0.30901699437494723, -0.9510565162951536, 0], [0.5358267949789968, -0.844327925502015, 0], [0.7289686274214119, -0.6845471059286883, 0], [0.8763066800438636, -0.4817536741017153, 0], [0.9685831611286312, -0.2486898871648545, 0]]]
        self.background_item = BackgroundItem(scene=self.scene, rows=self.table_rows, cols=self.table_cols,
                                              show_arrows=self.show_arrows, angle_field=self.angle_field)
        self.background_item.add_items_to_group(items)
        self.background_item.content = items
        self.scene.addItem(self.background_item)
        self.view.setScene(self.scene)
        self.setup_ghost()
        # self._initial_info = {}
        try:
            self._shared_data[SharedData.sensor_field] = [[0 for j in range(self.table_cols)] for i in
                                                          range(self.table_rows)]
        except TypeError:
            self._shared_data = {SharedData.sensor_field: [[0 for j in range(self.table_cols)] for i in
                                                           range(self.table_rows)]}

    def update_foreground_scene(self):
        self.scene.clear()
        self.update_background_scene()
        self.scene.addItem(self.background_item)
        self.view.setScene(self.scene)

    def update_background_scene(self):
        # same as setup but with different values of rows and cols, called from MainUi
        self.setup_background_scene()  # TODO: Call from MainUi instead

    def set_background_parameters(self, rows, cols, show_arrows):
        self.table_cols = cols
        self.table_rows = rows
        self.show_arrows = show_arrows
        self.update_background_scene()

    def mouse_hover(self, button: QPushButton):
        if button.isChecked():
            # start placing waypoints
            self.drawing = True
            self.coor_list.append([])

            # square is stuck to mouse, placed when clicked, won't stop until clicking on waypoint button or ESC key
        else:
            # stop placing waypoints and expect a list of waypoints
            # self.timer.stop()
            self.drawing = False
            self.last_point = None
            self.coor_index += 1

    def mousePressEvent(self, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton and self.drawing:
                # self.last_point = self.view.mapToScene(event.pos())
                current_point = self.get_cursor_position_in_view()
                t = [current_point.x(), current_point.y()]
                self.coor_list[self.coor_index].append(t)
                self.foldable_toolbar.manual_list_view.appendRow(QStandardItem(f"Waypoint at: ({round(t[0], 1)}, {round(t[1], 1)})"))
                # Create and show the rectangle on click
                self.create_and_show_rectangle(current_point)  # New function
                if self.last_point is not None:
                    line = QGraphicsLineItem(current_point.x(), current_point.y(), self.last_point.x(),
                                             self.last_point.y())
                    line.setPen(QPen(Qt.red, 2, Qt.DotLine, Qt.RoundCap, Qt.RoundJoin))
                    self.scene.addItem(line)
                self.last_point = current_point
        if self.objectName() == 'show_table':
            if event.type() == QEvent.MouseButtonPress and self.add_lanes.isChecked():
                direction = self.add_lanes_in_out.currentText()
                self.modify_lanes(add=True, position=self.get_cursor_position_in_view(), direction=direction)
            elif event.type() == QEvent.MouseButtonPress and self.remove_lanes.isChecked():
                direction = self.add_lanes_in_out.currentText()
                self.modify_lanes(add=False, position=self.get_cursor_position_in_view(), direction=direction)
            return None
        elif event.type() == QEvent.MouseButtonPress and self.select_start.isChecked():
            self._initial_info['start'] = \
                self.closest_grid_center(self.background_item.positions, self.get_cursor_position_in_view())[1]

        elif event.type() == QEvent.MouseButtonPress and self.select_end.isChecked():
            self._initial_info['end'] = \
                self.closest_grid_center(self.background_item.positions, self.get_cursor_position_in_view())[1]
        elif event.type() == QEvent.MouseButtonPress and self.select_obstacle.isChecked():
            if 'obstacle' not in self._initial_info.keys():
                self._initial_info['obstacle'] = []
            p = self.closest_grid_center(self.background_item.positions, self.get_cursor_position_in_view())[1]
            self._initial_info['obstacle'].append(p)
        logger.info(self._initial_info)
        self.highlight_after_depress()

    def modify_lanes(self, add: bool = True, position: float | None = None, direction: str | None = None):
        if add:
            closest_cell_center = \
                self.closest_grid_center(self.background_item.positions, self.get_cursor_position_in_view())[1]
            data_to_create_rep = self.background_item.modify_lanes(add=True, edge_cell_index=closest_cell_center,
                                                                   position=position, direction=direction)
            t = LaneGraphicRepresentation(*data_to_create_rep, count_for_name=len(self._lane_representation_list) + 1)
            if 'input' in t.name.lower():
                self.foldable_toolbar.input_lane.addItem(t.name)
            elif 'output' in t.name.lower():
                self.foldable_toolbar.output_lane.addItem(t.name)

            self._lane_representation_list.append(t)
            logger.info(f'We added lane {str(t)}')

        elif not add:
            mouse_pos = self.get_cursor_position_in_view()
            self.find_closest_rect_in_group(self.background_item, mouse_pos, )  # TODO: fix, good luck though
            #   self.background_item.modify_lanes(add=True, edge_cell_index=closest_cell_center, position=position, direction=direction)

    @staticmethod
    def find_closest_rect_in_group(group: QGraphicsItemGroup, mouse_pos: QPointF,
                                   threshold_rect: QRectF) -> QGraphicsRectItem | None:
        """
        This function finds the closest QGraphicsRectItem within a rectangular threshold from the mouse position in a QGraphicsItemGroup.

        Args:
            group: The QGraphicsItemGroup to search within.
            mouse_pos: The position of the mouse (QPointF).
            threshold_rect: The rectangular threshold defining the search area (QRectF).

        Returns:
            The closest QGraphicsRectItem within the threshold, or None if no items are found.
        """
        closest_item: QGraphicsRectItem | None = None
        closest_distance = float("inf")

        # Loop through child items of the group
        for child in group.children():
            if not isinstance(child, QGraphicsRectItem):
                continue  # Skip non-rect items

            # Check if item bounding rect intersects the threshold rect
            item_rect = child.boundingRect().translated(child.pos())
            if not item_rect.intersects(threshold_rect):
                continue  # Skip items outside threshold

            # Calculate distance between mouse and item center
            item_center = item_rect.center()
            distance = mouse_pos.distanceToPoint(item_center)

            # Update closest item if closer distance is found
            if distance < closest_distance:
                closest_distance = distance
                closest_item = child

                # Delete the closest item if found
            if closest_item is not None:
                group.removeItemGroup(closest_item)  # Remove from group
                del closest_item  # Delete the item object

    def get_cursor_position_in_view(self):
        # cursor_pos = win32api.GetCursorPos()
        # viewport_pos = self.view.viewport().mapToGlobal(QPoint(0, 0))
        # view_relative_pos = QPoint(cursor_pos[0] + viewport_pos.x(), cursor_pos[1] + viewport_pos.y())
        # pos = QCursor.pos()  #viewport().mapFromGlobal | mapToScene
        # pos_2 = self.view.viewport().mapFromGlobal(QCursor.pos())  #viewport().mapFromGlobal | mapToScene

        pos = self.view.viewport().mapFromGlobal(QCursor.pos())  # Get viewport that is GraphicView
        scene_pos = self.view.mapToScene(pos)  # Get scene coordinates, with respect to scrolling and same plane as hex
        return scene_pos

    @staticmethod
    def closest_grid_center(grid_centers: list[list[list]], point):
        min_distance = float('inf')
        closest_center = None
        closest_indices = None

        # Iterate through each row in the 2D array
        for i, row in enumerate(grid_centers):
            # Iterate through each grid center in the row
            for j, center in enumerate(row):
                # Calculate the distance between the current grid center and the point
                distance = math.sqrt((center[0] - point.x()) ** 2 + (center[1] - point.y()) ** 2)

                # Update the closest center if the current distance is smaller
                if distance < min_distance:
                    min_distance = distance
                    closest_center = center
                    closest_indices = (i, j)

        return [closest_center, closest_indices]

    @property
    def initial_info(self):
        return self._initial_info

    @property
    def foldable_toolbar(self):
        return self._foldable_toolbar

    @property
    def lane_representation_list(self):
        return self._lane_representation_list

    @lane_representation_list.setter
    def lane_representation_list(self, value):
        self._lane_representation_list = value

    @foldable_toolbar.setter
    def foldable_toolbar(self, value):
        self._foldable_toolbar = value

    def update_and_draw_rectangle(self):  # obsolete
        # TODO: solve rect offset issues
        return None  # TODO: Fix the offset and delete this later
        cursor_pos: QPointF = self.get_cursor_position_in_view()
        if self.drag_rectangle is None:
            self.drag_rectangle = QGraphicsRectItem(cursor_pos.x(), cursor_pos.y(), self._package_size,
                                                    self._package_size)  # Set width and height
            self.drag_rectangle.setBrush(Qt.red)
            self.drag_rectangle.setPen(Qt.green)
            self.scene.addItem(self.drag_rectangle)

        self.drag_rectangle.setPos(cursor_pos.x(), cursor_pos.y())
        self.drag_rectangle.setVisible(True)

    def create_and_show_rectangle(self, current_point):
        drag_rectangle = QGraphicsRectItem(current_point.x() - self._package_size / 2,
                                           current_point.y() - self._package_size / 2, self._package_size,
                                           self._package_size)  # TODO: exclude squares from clear while waypoint ON
        drag_rectangle.setBrush(Qt.red)
        drag_rectangle.setPen(Qt.green)
        self.scene.addItem(drag_rectangle)

    def draw_on_scene(self, start_point, end_point):  # TODO: Obsolete, delete later
        # Draw on the foreground scene
        color = QColor(Qt.red, 255, 255, int(255 * 0.5))
        pen = QPen(color, self._package_size, Qt.DotLine, Qt.RoundCap, Qt.RoundJoin)
        path = QPainterPath()
        path.moveTo(start_point)
        path.lineTo(end_point)
        self.scene.addPath(path, pen)
        self.paths[self.path_index].append(path)
        self.scene.addItem(self.background_item)
        self.view.setScene(self.scene)

    def change_pen_size(self, val):
        self._package_size = val

    @property
    def pen_size(self):
        return self._package_size

    def set_foldable_bar(self, val):
        self.foldable_toolbar: FoldableToolBar = val

    def show_ghost(self, button: QPushButton):
        if button.isChecked():
            self.show_ghost_simulation = True
        else:
            self.show_ghost_simulation = False


class MainUi(QMainWindow):
    sensor_refresh_rate = 1000  # ms

    def __init__(self, robot: Robot, *args, **kwargs):
        super(MainUi, self).__init__(*args, **kwargs)
        self.cell_grid = None
        ui_filename = rf'{os.path.realpath(os.path.dirname(__file__))}\ui_files\window_0_1.ui'
        loadUi(ui_filename, self)
        try:
            self._default_values = self.robot.default_values
        except:
            self._default_values = None
        standard_sheet = "standard_style_sheet.qss"
        dark_sheet = "QTDark.stylesheet"
        # Load the stylesheet
        with open(rf"{os.path.realpath(os.path.dirname(__file__))}\ui_files\{standard_sheet}", 'r') as f:
            stylesheet = f.read()

        # Apply the stylesheet to the main window
        self.setStyleSheet(stylesheet)
        self.resize(1366, 768)
        self.robot = robot
        self.show_arrows = False
        self.stackedWidget_3000: QStackedWidget = self.findChild(QStackedWidget, "stackedWidget_3000")
        self.stackedWidget_3000.setCurrentIndex(1)
        self.table_preview: Table_preview = self.findChild(QWidget, 'show_table')
        self.table_preview_2: Table_preview = self.findChild(QWidget, 'table_draw_enabled')
        self.table_preview.set_main(self)
        self.table_preview_2.set_main(self)

        self.foldable_toolbar = self.findChild(QWidget, 'FoldableToolBar')
        self.table_preview.foldable_toolbar = self.foldable_toolbar
        self.table_preview_2.foldable_toolbar = self.foldable_toolbar

        self.initialize()

    def initialize(self):
        start = self.findChild(QPushButton, 'start')
        end = self.findChild(QPushButton, 'end')
        obstacle = self.findChild(QPushButton, 'obstacle')
        self.table_preview_2.setup_auto_button(start, end, obstacle)
        self.setFocusPolicy(Qt.StrongFocus)
        self.installEventFilter(self)
        self.set_triggers()
        self.set_default_values()
        self.set_table_preview()
        self.set_menu()

    @pyqtSlot()
    def open_file(self, option, filextension, dialog_type):
        dialog_method = QFileDialog.getOpenFileName if dialog_type != "save" else QFileDialog.getSaveFileName
        if filextension == 'dae':
            extension_filter = 'Collada (*.dae)'
        elif filextension == 'py':
            extension_filter = 'Controller (*.py)'
        else:
            extension_filter = 'All Files (*)'
        file_path, _ = dialog_method(parent=self, caption=f"{option}", directory=self.default_values['cwd'],
                                     filter=extension_filter)
        if file_path:
            # If a file is selected, display its path
            self.statusBar().showMessage(f"{option}: {file_path}")

    def set_menu(self):
        self.actionChasis.triggered.connect(lambda: self.open_file('Chassis', 'dae', 'open'))
        self.actionWheel.triggered.connect(lambda: self.open_file('Wheel', 'dae', 'open'))
        self.actionController.triggered.connect(lambda: self.open_file('Controller', 'py', 'open'))
        self.actionWebot_world_file.triggered.connect(lambda: self.open_file('Controller', 'py', 'save', 'open'))

        self.actionEdit_table_data.triggered.connect(lambda: self.switch_menu(self.actionEdit_table_data))  # 1
        self.actionPath_and_preview.triggered.connect(lambda: self.switch_menu(self.actionPath_and_preview))  # 0

        self.actionShow_arrows.triggered.connect(self.display_arrows)
        self.actionPath_and_preview.setObjectName('draw_screen')
        self.actionEdit_table_data.setObjectName('preview_screen')

        self.actionShow_ghost.triggered.connect(lambda: self.table_preview_2.show_ghost(self.actionShow_ghost))

    def switch_menu(self, action=None):
        if not action:
            if self.stackedWidget_3000.currentIndex() == 1:
                self.stackedWidget_3000.setCurrentIndex(0)
                content_from_other_table = self.table_preview.background_item.content
                self.table_preview_2.setup_background_scene(content_from_other_table)
                self.table_preview_2.lane_representation_list = self.table_preview.lane_representation_list

            else:
                self.stackedWidget_3000.setCurrentIndex(1)

        elif action.objectName() == 'draw_screen':
            content_from_other_table = self.table_preview.background_item.content
            self.table_preview_2.setup_background_scene(content_from_other_table)
            self.table_preview_2.lane_representation_list = self.table_preview.lane_representation_list

            action.setChecked(True)
            self.actionEdit_table_data.setChecked(False)
            self.stackedWidget_3000.setCurrentIndex(0)
        elif action.objectName() == 'preview_screen':
            action.setChecked(True)
            self.actionPath_and_preview.setChecked(False)
            self.stackedWidget_3000.setCurrentIndex(1)

    def display_arrows(self):
        if self.actionShow_arrows.isChecked():
            self.show_arrows = True
        else:
            self.show_arrows = False
        self.update_table_preview()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backslash:
            self.switch_menu()
        else:
            super().keyPressEvent(event)

    def reload_dicts(self):
        x = self.row_count.value()
        y = self.col_count.value()
        logger.info("Created the dictionary")
        data = {SharedData.sensor_field: [[0 for i in range(x)] for j in range(y)],
                SharedData.vector_field: [[[0, 0, 0] for i in range(x)] for j in range(y)],
                SharedData.simulation_information: {'rows': x, 'cols': y}}

        shared_mem.store_data(data=data)

    def set_triggers(self):
        self.create_progressBar: QProgressBar = self.findChild(QProgressBar, "create_progressBar")
        self.create_progressBar.setValue(0)
        self.button_create.clicked.connect(self.create_webot_world_file)
        self.row_count.valueChanged.connect(self.update_table_preview)
        self.col_count.valueChanged.connect(self.update_table_preview)
        self.foldable_toolbar.package_size_spin_box.valueChanged.connect(
            lambda: self.table_preview_2.change_pen_size(self.foldable_toolbar.package_size_spin_box.value()))
        self.foldable_toolbar: FoldableToolBar
        t = self.foldable_toolbar.waypoint_pins
        t.clicked.connect(lambda: self.table_preview_2.mouse_hover(t))
        self.table_preview_2.set_foldable_bar(self.foldable_toolbar)

        self.reload_dicts()

    def update_table_preview(self):  # TODO: deprecated, remove later
        raduis = 20
        self.scene = QGraphicsScene()
        self.brush_blue = QBrush(Qt.blue)
        self.pen = QPen()
        self.table_preview.set_background_parameters(rows=self.row_count.value(), cols=self.col_count.value(),
                                                     show_arrows=self.show_arrows)
        self.table_preview_2.set_background_parameters(rows=self.row_count.value(), cols=self.col_count.value(),
                                                       show_arrows=self.show_arrows)
        # self.Table_preview.setScene(self.scene)
        self.reload_dicts()

    def create_webot_world_file(self):
        # TODO: connect clicking the button with extracting all the values from the UI
        self.create_progressBar.setValue(0)
        try:

            self.robot.dimensions.x = self.row_count.value()
            self.robot.dimensions.y = self.col_count.value()

            self.robot.filename = self.filename_name.text()
            self.robot.controller = self.controller_name.text()
            self.robot.lane_data = self.table_preview.background_item.content
        except Exception as e:
            logger.info(e)
        t = 0
        while t <= 100:
            t += 1
            self.create_progressBar.setValue(t)
        self.robot.create_file()

    def set_default_values(self):
        self.filename_name.setText(self.robot.filename)
        self.controller_name.setText(self.robot.controller)

        self.row_count.setValue(self.robot.dimensions.x)
        self.col_count.setValue(self.robot.dimensions.y)

        # self.robot.get_filename()
        # TODO: set table tran, rot, dimen .... default

    def set_table_preview(self):
        self.calculate_button: QPushButton = self.findChild(QPushButton, 'calculate_button')
        self.launch_button: QPushButton = self.findChild(QPushButton, 'launch_button')
        self.launch_button.clicked.connect(lambda: self.communicate_with_simulation(self.launch_button))
        self.tab_area: QTabWidget = self.findChild(QTabWidget, 'Edit_area_tab')
        # TODO: When launch is checked:
        #   - Supervisor communicates with QtGui
        #   - Starts monitoring sensor data and updates cell highlight state

    def communicate_with_simulation(self, button):
        # TODO: When launch is checked:
        #   - Supervisor communicates with QtGui
        #   - Starts monitoring sensor data and updates cell highlight state

        # TODO: For automatic pathing:
        logger.debug(f"Launched the supervisor")
        #subprocess.call(['python', r'C:\Users\toupa\Desktop\ESE - S1\PFE\3D\New folder\controllers\cell_controller_0_3\cell_controller_0_3.py'])
        logger.info('Launching')
        if button.isChecked() and self.tab_area.currentIndex() == 0:
            # when launching is checked the manual tab widget is active
            self.get_sensor_data_timer = QTimer()
            self.get_sensor_data_timer.setInterval(MainUi.sensor_refresh_rate)
            self.get_sensor_data_timer.timeout.connect(self.table_preview_2.update_package_location)
            self.get_sensor_data_timer.start()
        elif not button.isChecked() and self.tab_area.currentIndex() == 0:
            # abort launch for manual pathing
            self.get_sensor_data_timer.stop()
        elif button.isChecked() and self.tab_area.currentIndex() == 1:
            # When launch in automatic mode
            self.get_sensor_data_timer = QTimer()
            self.get_sensor_data_timer.setInterval(MainUi.sensor_refresh_rate)
            self.get_sensor_data_timer.timeout.connect(self.table_preview_2.update_package_location)
            self.get_sensor_data_timer.start()
            self.calculate_automatic_pathing(True)
        elif not button.isChecked() and self.tab_area.currentIndex() == 1:
            self.get_sensor_data_timer.stop()
        elif button.isChecked() and self.tab_area.currentIndex() == 2:
            # When launch in automatic mode
            self.get_sensor_data_timer = QTimer()
            self.get_sensor_data_timer.setInterval(MainUi.sensor_refresh_rate)
            self.get_sensor_data_timer.timeout.connect(self.table_preview_2.update_package_location)
            self.get_sensor_data_timer.start()
            self.calculate_automatic_pathing(True)
        elif not button.isChecked() and self.tab_area.currentIndex() == 2:
            self.get_sensor_data_timer.stop()

    def calculate_automatic_pathing(self, enabled):
        if enabled:
            global shared_mem
            self.table_preview_2: Table_preview
            # Get the grid
            grid = self.table_preview_2.background_item.obstacle
            # Get start and end positions
            d = self.table_preview_2.initial_info
            if 'end' not in d.keys() and 'start' not in d.keys():
                logger.info(F"select start & end")
                return None

            '''start = d['start']
            end = d['end']

            # do the calculation
            self.cell_grid = CelluvoyerGrid(grid)
            paths = CelluvoyerGrid.a_star_search(self.cell_grid, start, end, max_paths=2)
            assert start in paths[0] and end in paths[0], "start and end not in paths"
            self.table_preview_2.background_item.highlight_list(paths[0])
            t = self.table_preview_2.initial_info
            logger.info(f"The final path is: {paths}")
            # show arrows + highlight:
            # TODO: Inside this, create vector field and return it then save it to shared mem
            self.table_preview_2.background_item.draw_path_arrows(paths[0],
                                                                  lane_list=self.table_preview.lane_representation_list)
            self.table_preview_2.background_item.highlight_point(t)
            # send the command
            logger.info("Sent command to simulation")
            d = shared_mem.retrieve_data()
            d[SharedData.vector_field] = self.table_preview_2.background_item.vector_field
            d[SharedData.simulation_information]['rows'] = len(grid)
            d[SharedData.simulation_information]['cols'] = len(grid[0])
            shared_mem.store_data(d)
            logger.info(f"After creating the commands, this is the data: {d}")'''
            # wait for feedback

    @property
    def default_values(self):
        return self._default_values


if __name__ == '__main__':
    app = QApplication(sys.argv)
    r = Robot(translation=[0, 0, 0.1], dimensions=[5, 5], rotation=[0, 0, 1, 0], controller=r'cell_controller_0_2')
    ui = MainUi(r)
    ui.show()
    app.exec_()
