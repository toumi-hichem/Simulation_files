import json
import math
import pickle
from shared_data import SharedData

# import statsmodels.api as sm
import win32api
from math import cos, sin, radians
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QSizePolicy, QListView, QGraphicsPixmapItem, QComboBox, \
    QProgressBar, QTabWidget
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


# TODO: Create a cell editor table for color, dimensions ....
# TODO: Write a setup.
# TODO: maybe even exclude individual engines if not inside bounds to save energy, need hexagon class
# TODO: Handle multiple packages


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
            angle_rad = radians(angle_deg)
            x = self.center_x + self.hex_size * cos(angle_rad)
            y = self.center_y + self.hex_size * sin(angle_rad)
            points.append(QPointF(x, y))
        return QPolygonF(points)

    def style_hex(self):
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)

    def create_arrow(self, vector_dir=None):
        if not vector_dir:
            vector_dir = self.vector_dir
        if not self.show_arrows:
            self._arrow = []
            self._content = [self, ] + self._arrow
            return None
        self.style_arrow()
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

    def style_arrow(self):
        self.vector_pen = QPen(QColor("yellow"))

    def specific_highlight(self, s_e):
        print(f"Highlight: {s_e}")
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


class BackgroundItem(QGraphicsItemGroup):  # QGraphicsPolygonItem
    def __init__(self, scene, rows, cols, cell_width, cell_height, show_arrows, path=None, angle_field=None):
        super().__init__()
        # 0, 0, cols * cell_width, rows * cell_height
        self.scene = scene
        self.angle_field = angle_field
        self.path = path


        self.hex_size = 40  # Size of hexagons
        self.x_spacing = self.hex_size * 1.7
        self.y_spacing = self.hex_size * 1.5
        self.vector_length = self.hex_size / 2

        self.rows = rows
        self.cols = cols
        self.initial_pos_x = self.rows * self.hex_size * 0.5
        self.initial_pos_y = self.cols * self.hex_size * 0.5

        self._positions = []
        self._hexs_: list[list[Hexagon]] = []
        self._obstacle: list[list[int]] = []
        self._selected: list[list[int]] = []

        # create_stuff
        for i in range(self.rows):
            self._positions.append([])
            for j in range(self.cols):
                center_x = self.initial_pos_x + self.x_spacing * i + (self.hex_size * 0.9 if j % 2 == 0 else 0)
                center_y = self.initial_pos_y + self.y_spacing * j
                self._positions[i].append([center_x, center_y])

        self.vector_pen = QPen(QColor("yellow"))
        self.vector_brush = QBrush(QColor('blue'))
        self.vector_dir = math.pi

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
    def hexs(self):
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
        for line in range(len(self.hexs)):
            self._obstacle.append([])
            for cell in range(len(self.hexs[line])):
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
                        print("obstacle")
                        self.hexs[cell][line].obstacle = 1
                    print(f"Total highlight calls: {t}")
        if isinstance(cor, tuple|list):
            print(f"manual highlight, {s_e}")
            if obstacle:
                t = self.hexs[cor[0]][cor[1]].obstacle
                self.hexs[cor[0]][cor[1]].obstacle = not t if flip else t
            else:
                self.hexs[cor[0]][cor[1]].specific_highlight(s_e)

    def create_table(self):
        drawing_path, current_index, future_index = False, 0, 1
        if self.path:
            drawing_path = True
        self._hexs_ = []
        for i in range(self.rows):
            self._hexs_.append([])
            for j in range(self.cols):
                center_x = self.initial_pos_x + self.x_spacing * i + (self.hex_size * 0.9 if j % 2 == 0 else 0)
                center_y = self.initial_pos_y + self.y_spacing * j
                show_arrows = self.show_arrows
                # Displaying the vector
                if drawing_path:
                    if (i, j) in self.path:
                        current_index = self.path.index((i, j))
                        if current_index == len(self.path) - 1:
                            show_arrows = False
                            self.vector_dir = None
                        else:
                            x_end, y_end = self.path[current_index]
                            x_start, y_start = self.path[current_index + 1]

                            x_end, y_end = self.positions[x_end][y_end]
                            x_start, y_start = self.positions[x_start][y_start]

                            t = [x_start - x_end, y_start - y_end]
                            vector = np.array(t)
                            angle_rad = np.arccos(
                                np.dot(vector, [1, 0]) / (np.linalg.norm(vector) * np.linalg.norm([1, 0])))
                            angle_rad = math.atan2(t[1], t[0])
                            self.vector_dir = angle_rad
                    else:
                        show_arrows = False
                        self.vector_dir = None
                elif self.angle_field is not None:
                    t = self.angle_field[i][j]
                    if t[0] is None:
                        self.vector_dir = None
                    else:
                        vector = np.array(t)
                        angle_rad = np.arccos(
                            np.dot(vector, [1, 0]) / (np.linalg.norm(vector) * np.linalg.norm([1, 0])))
                        self.vector_dir = angle_rad

                hexagon = Hexagon(center_x, center_y, vector_dir=self.vector_dir, show_arrows=show_arrows)
                hexagon.obstacle = 0
                self._hexs_[i].append(hexagon)
        self.add_items_to_group()

    def add_items_to_group(self):
        for line in range(len(self.hexs)):
            for cell in range(len(self.hexs[line])):
                for item in self.hexs[line][cell].content:
                    self.addToGroup(item)

    def draw_path_arrows(self, cell_list: list[list[int, int]]):
        self.path = cell_list
        self.create_table()


class Table_preview(QWidget):
    json_vec_field_filename = r'C:\Users\toupa\Desktop\ESE - S1\PFE\3D\New folder\controllers\dataexchange.pkl'

    def __init__(self, *args):
        super().__init__(*args)
        self.select_start = None
        self.select_end = None
        self.select_obstacle = None
        print(F"Accessing shared data named: {SharedData.shrm_name}")
        try:
            self.shared_mem = SharedData(name=SharedData.shrm_name, create=True)
        except FileExistsError:
            self.shared_mem = SharedData(name=SharedData.shrm_name, create=False)
        self._shared_data = {}
        self._initial_info = {}

        self.drag_rectangle = None
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._package_size = 20
        self.show_arrows = False
        self.angle_field = None
        self._package_size = 60

        # hover constants
        self.hover_with_mouse = False

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

        # TODO: get dimension_x and _y from MainUi and save then as self.cols etc then run the entire update to the preview
        # self.update_button.clicked.connect(self.update_background_scene)

        self.setup_buttons()

        # Variables to track drawing
        self.last_point = None
        self.drawing = False

    def update_package_location(self):
        # TODO: Use QTimer, maybe 200ms? More, focus on performance, sim is too slow anyways.
        # TODO: create supervisor to place objects as well as know when simulation is finished, need info dict in shrm
        """Runs periodically using QTimer.
            Extracts sensor data from shared memory and updates hexagon highlight state.
            Will be first launched after self.launched_button is triggered.
            """
        try:
            self._shared_data = self.shared_mem.retrieve_data()
            self.background_item: BackgroundItem
            self.background_item.hexs = self._shared_data[SharedData.sensor_field]
        except:
            print("Simulation is offline")

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

    def save_vec_field_data(self):
        # TODO: This only saves one list at a time, fix later
        t = self.numpy_array_to_list(self.angle_field)
        with open(self.json_vec_field_filename, 'wb') as f:
            pickle.dump(t, f)

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
        self.shared_mem.store_data(self._shared_data)
        self.update_background_scene()  # TODO: Create option not to delete rects + lines
        self.save_vec_field_data()

        self.scene.addItem(self.background_item)
        self.view.setScene(self.scene)

    def create_vector_field(self, path_points, vec_fiel, x, y):
        vector_field = [[0 for j in range(y)] for i in range(x)]
        for i in range(len(vec_fiel)):
            for j in range(len(vec_fiel[0])):
                cell = vec_fiel[i][j]
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
            return closest_tangent / magnitude
        else:
            return None, None

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

    def launch_controller(self):
        self.main_window.robot.launch_controller_string(1, 1, 0)
        pass

    def setup_background_scene(self):  # TODO: implement to be called from MainUi using dimension_x inputs
        cell_width = 50
        cell_height = 50
        self.background_item = BackgroundItem(self.scene, self.table_rows, self.table_cols, cell_width, cell_height,
                                              self.show_arrows, self.angle_field)
        self.background_item.clear_all_highlight()
        self.scene.clear()
        self.scene.addItem(self.background_item)
        self.view.setScene(self.scene)
        self._initial_info = {}
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
                # Create and show the rectangle on click
                self.create_and_show_rectangle(current_point)  # New function
                if self.last_point is not None:
                    line = QGraphicsLineItem(current_point.x(), current_point.y(), self.last_point.x(),
                                             self.last_point.y())
                    line.setPen(QPen(Qt.red, 2, Qt.DotLine, Qt.RoundCap, Qt.RoundJoin))
                    self.scene.addItem(line)
                self.last_point = current_point
        if self.objectName() == 'show_table':
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
        self.highlight_after_depress()

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

    def update_and_draw_rectangle(self):
        # TODO: solve rect offset issues
        return None  # TODO: Fix the offset and delete this later
        cursor_pos = self.get_cursor_position_in_view()
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


class FoldableToolBar(QWidget):
    def __init__(self, parent=None):
        super(FoldableToolBar, self).__init__(parent)
        self.package_size_spin_box = None
        self.setObjectName("FoldableToolBar")
        self.is_collapsed = False

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(300)
        self.layout = QHBoxLayout(self)
        self.header_label = QPushButton(">")
        self.header_label.setFixedSize(30, 70)
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.content_widget.setMinimumWidth(200)

        self.layout.addWidget(self.header_label)
        self.header_label.clicked.connect(self.toggle_collapse)

        self.set_content()

    def set_content(self):
        self.tab = QTabWidget()
        self.tab.setObjectName("Edit_area_tab")
        self.tab_manual = QWidget()
        self.tab_auto = QWidget()
        self.tab.addTab(self.tab_manual, "Manual")
        self.tab.addTab(self.tab_auto, "Automatic")
        # manual Tab
        lay = QVBoxLayout(self.tab_manual)
        # box size spin box
        self.package_size_spin_box = QSpinBox()
        self.package_size_spin_box.setMinimum(10)
        self.package_size_spin_box.setValue(60)
        self.package_size_spin_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.spin_box_label = QLabel("Package size: ")
        hspin_label_lay = QHBoxLayout()
        hspin_label_lay.addWidget(self.spin_box_label)
        hspin_label_lay.addWidget(self.package_size_spin_box)
        self.spin_box_label_widget = QWidget()
        self.spin_box_label_widget.setLayout(hspin_label_lay)
        # button to start putting waypoints
        self.waypoint_pins = QPushButton("Waypoints")

        self.waypoint_pins.setCheckable(True)

        self.pick_wayp_list = QComboBox()
        self.pick_wayp_list.addItem("Waypoint - 1")
        self.pick_wayp_list.addItem("Waypoint - 2")

        self.list_view = QListView()
        self.model = QStandardItemModel()  # TODO: Create a signal to know when a box has been created to insert to listview
        item1 = QStandardItem("Waypoint point - 1")
        item2 = QStandardItem("Waypoint point - 2")
        self.model.appendRow(item1)
        self.model.appendRow(item2)
        self.list_view.setModel(self.model)

        # fill the layout
        lay.addWidget(self.spin_box_label_widget)
        lay.addWidget(self.waypoint_pins)
        lay.addWidget(self.pick_wayp_list)  # TODO: connect indexChanged to model listview different self.coor_list
        lay.addWidget(self.list_view)

        # automatic Tab
        lay_a = QVBoxLayout(self.tab_auto)
        self.automatic_paths = QComboBox()
        self.automatic_list = QListView()
        self.automatic_model = QStandardItemModel()

        self.select_start = QPushButton('start')
        self.select_end = QPushButton('end')
        self.select_obstacle = QPushButton('obstacle')
        self.select_start.setCheckable(True)
        self.select_end.setCheckable(True)
        self.select_obstacle.setCheckable(True)
        self.select_start.setObjectName('start')
        self.select_end.setObjectName('end')
        self.select_obstacle.setObjectName('obstacle')

        self.auto_button_w = QWidget()
        self.auto_button_lay = QHBoxLayout(self.auto_button_w)
        self.auto_button_lay.addWidget(self.select_start)
        self.auto_button_lay.addWidget(self.select_end)
        self.auto_button_lay.addWidget(self.select_obstacle)

        self.automatic_list.setModel(self.automatic_model)

        self.auto_package_size_spin_box = QSpinBox()
        self.auto_package_size_spin_box.setMinimum(10)
        self.auto_package_size_spin_box.setValue(60)
        self.auto_package_size_spin_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.auto_spin_box_label = QLabel("Package size: ")
        auto_hspin_label_lay = QHBoxLayout()
        auto_hspin_label_lay.addWidget(self.auto_spin_box_label)
        auto_hspin_label_lay.addWidget(self.auto_package_size_spin_box)
        self.auto_spin_box_label_widget = QWidget()
        self.auto_spin_box_label_widget.setLayout(auto_hspin_label_lay)

        lay_a.addWidget(self.auto_spin_box_label_widget)
        lay_a.addWidget(self.auto_button_w)
        lay_a.addWidget(self.automatic_paths)
        lay_a.addWidget(self.automatic_list)

        self.layout.addWidget(self.tab)

    def insert_item_to_list(self, item, manual=True, path=False):
        if manual and not path:
            self.model.appendRow(QStandardItemModel(item))
        elif not manual and not path:
            self.automatic_model.appendRow(QStandardItemModel(item))
        elif manual and path:
            self.pick_wayp_list.addItem(item)
        elif not manual and path:
            self.automatic_paths.addItem(item)

    def toggle_collapse(self):
        if self.is_collapsed:
            # self._expand_animation()
            self.tab.show()
            self.setMaximumWidth(400)  # TODO: width too big, change after adding all widget to something smaller
            self.setMinimumWidth(400)
            self.header_label.setText(">")
        else:
            # self._collapse_animation()
            self.tab.hide()
            self.setMaximumWidth(50)
            self.setMinimumWidth(50)
            self.header_label.setText("<")
        self.is_collapsed = not self.is_collapsed

    def _collapse_animation(self):
        print(f"_collapse_animation, width: {self.tab.width()}")
        animation = QPropertyAnimation(self.tab, b"minimumWidth")
        animation.setDuration(250)
        animation.setStartValue(self.tab.width())
        animation.setEndValue(50)
        animation.setEasingCurve(QEasingCurve.Linear)
        animation.finished.connect(lambda: self.tab.hide())
        animation.start()

    def _expand_animation(self):
        print(f"_expand_animation, width: {self.tab.width()}")
        animation = QPropertyAnimation(self.tab, b"minimumWidth")
        animation.setDuration(250)
        animation.setStartValue(0)
        animation.setEndValue(self.tab.width())
        animation.setEasingCurve(QEasingCurve.Linear)
        animation.finished.connect(lambda: self.tab.show())
        animation.start()


class MainUi(QMainWindow):
    sensor_refresh_rate = 200  # ms

    def __init__(self, robot: Robot):
        super(MainUi, self).__init__()
        self.cell_grid = None
        ui_filename = r'C:\Users\toupa\Desktop\ESE - S1\PFE\Simulation_files\ui_files\window_0_1.ui'
        loadUi(ui_filename, self)
        self.resize(1366, 768)
        self.robot = robot
        self._default_values = self.robot.default_values
        self.show_arrows = False
        self.stackedWidget_3000: QStackedWidget = self.findChild(QStackedWidget, "stackedWidget_3000")
        self.stackedWidget_3000.setCurrentIndex(1)
        self.table_preview: Table_preview = self.findChild(QWidget, 'show_table')
        self.table_preview_2: Table_preview = self.findChild(QWidget, 'table_draw_enabled')
        self.foldable_toolbar = self.findChild(QWidget, 'FoldableToolBar')

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

    def switch_menu(self, action=None):
        if not action:
            if self.stackedWidget_3000.currentIndex() == 1:
                self.stackedWidget_3000.setCurrentIndex(0)
            else:
                self.stackedWidget_3000.setCurrentIndex(1)

        elif action.objectName() == 'draw_screen':
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

    def set_triggers(self):
        self.create_progressBar: QProgressBar = self.findChild(QProgressBar, "create_progressBar")
        self.create_progressBar.setValue(0)
        self.button_create.clicked.connect(self.create_webot_world_file)
        self.dimension_x.valueChanged.connect(self.update_table_preview)
        self.dimension_y.valueChanged.connect(self.update_table_preview)
        self.foldable_toolbar.package_size_spin_box.valueChanged.connect(
            lambda: self.table_preview_2.change_pen_size(self.foldable_toolbar.package_size_spin_box.value()))

    def update_table_preview(self):  # TODO: deprecated, remove later
        raduis = 20
        self.scene = QGraphicsScene()
        self.brush_blue = QBrush(Qt.blue)
        self.pen = QPen()
        self.table_preview.set_background_parameters(self.dimension_x.value(), self.dimension_y.value(),
                                                     self.show_arrows)
        self.table_preview_2.set_background_parameters(self.dimension_x.value(), self.dimension_y.value(),
                                                       self.show_arrows)
        # self.Table_preview.setScene(self.scene)

    def create_webot_world_file(self):
        # TODO: connect clicking the button with extracting all the values from the UI
        self.create_progressBar.setValue(0)
        self.robot.translation.x = float(self.location_x.text())
        self.robot.translation.y = float(self.location_y.text())
        self.robot.translation.z = float(self.location_z.text())
        try:
            self.robot.rotation.x = self.rotation_x.value()
            self.robot.rotation.y = self.rotation_y.value()
            self.robot.rotation.z = self.rotation_z.value()
            self.robot.rotation.o = self.rotation_o.value()

            self.robot.dimensions.x = self.dimension_x.value()
            self.robot.dimensions.y = self.dimension_y.value()

            self.robot.filename = self.filename_name.text()
            self.robot.controller = self.controller_name.text()
        except Exception as e:
            print(e)
        t = 0
        while t <= 100:
            t += 1
            self.create_progressBar.setValue(t)
        self.robot.create_file()

    def set_default_values(self):
        self.filename_name.setText(self.robot.filename)
        self.controller_name.setText(self.robot.controller)

        self.location_x.setValue(self.robot.translation.x)
        self.location_y.setValue(self.robot.translation.y)
        self.location_z.setValue(self.robot.translation.z)

        self.rotation_x.setValue(self.robot.rotation.x)
        self.rotation_y.setValue(self.robot.rotation.y)
        self.rotation_z.setValue(self.robot.rotation.z)
        self.rotation_o.setValue(self.robot.rotation.o)

        self.dimension_x.setValue(self.robot.dimensions.x)
        self.dimension_y.setValue(self.robot.dimensions.y)

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

    def calculate_automatic_pathing(self, enabled):
        if enabled:
            self.table_preview_2: Table_preview
            # Get the grid
            grid = self.table_preview_2.background_item.obstacle
            print(f"The grid is: {grid}")
            # Get start and end positions
            self.table_preview_2: FoldableToolBar
            d = self.table_preview_2.initial_info
            start = d['start']
            end = d['end']

            # do the calculation
            self.cell_grid = CelluvoyerGrid(grid)
            paths = CelluvoyerGrid.a_star_search(self.cell_grid, start, end, max_paths=2)
            self.table_preview_2.background_item.highlight_list(paths[0])
            t = self.table_preview_2.initial_info
            print(f"The final path is: {paths}")
            # show arrows + highlight:
            self.table_preview_2.background_item.draw_path_arrows(paths[0])
            self.table_preview_2.background_item.highlight_point(t)
            # send the command

            # wait for feedback

    @property
    def default_values(self):
        return self._default_values


if __name__ == '__main__':
    app = QApplication(sys.argv)
    r = Robot(translation=[0, 0, 0.1], dimensions=[5, 5], rotation=[0, 0, 1, 0], controller=r'<extern>')
    ui = MainUi(r)
    ui.show()
    app.exec_()
