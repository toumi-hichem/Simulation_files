import json
import math
import pickle

# import statsmodels.api as sm
import win32api
from math import cos, sin, radians
from math import sqrt as sq
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QSizePolicy, QListView, QGraphicsPixmapItem, QComboBox, \
    QProgressBar
import sys
from WBWorldGenerator import Robot
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsView, QVBoxLayout, QPushButton, QSpinBox, \
    QLabel, QGraphicsLineItem, QHBoxLayout, QGraphicsRectItem, QFileDialog, QStackedWidget, QGraphicsPolygonItem, \
    QGraphicsItemGroup
from PyQt5.QtGui import QBrush, QPen, QPolygonF, QPainter, QImage, QPixmap, QPainterPath, QColor, QStandardItem, \
    QStandardItemModel, QCursor, QGuiApplication, QTransform
from PyQt5.QtCore import Qt, QPointF, QLineF, QEvent, QRectF, pyqtSlot, QPropertyAnimation, QAbstractAnimation, \
    QEasingCurve, QTimer, QPoint


# TODO: Create a side tab which varies the mouse painter size to accommodate different package sizes.
# TODO: Write a setup.
# TODO: If two straight path crossed, take their average instead of one over the other.
# TODO: maybe even exclude individual engines if not inside bounds to save energy, need hexagon class
# TODO: Math for the speed of a package with mass m above the cell
# TODO: Touchsensor
# TODO: Package tracking with touchsensor
# TODO: Handle multiple packages
# TODO:

def get_hexagon(x, y, length):
    starting_angle = 30
    angle_between = 60
    poly = QPolygonF()

    for i in range(6):
        poly << QPointF(cos(radians(starting_angle + angle_between * i)),
                        sin(radians(starting_angle + angle_between * i)))
    return poly


class BackgroundItem(QGraphicsItemGroup):  # QGraphicsPolygonItem
    def __init__(self, scene, rows, cols, cell_width, cell_height, show_arrows, angle_field=None):
        super().__init__()
        # 0, 0, cols * cell_width, rows * cell_height
        self.scene = scene
        self.angle_field = angle_field
        self.hex_size = 40  # Size of hexagons
        self.spacing = -100  # Spacing between hexagons
        self.x_spacing = self.hex_size * 1.7
        self.y_spacing = self.hex_size * 1.5
        self.vector_length = self.hex_size / 2
        self._positions = []

        self.vector_pen = QPen(QColor("yellow"))
        self.vector_brush = QBrush(QColor('blue'))
        self.vector_dir = math.pi

        self.pen = QPen(QColor("green"))
        self.brush = QBrush(QColor('blue'))

        self.show_arrows = show_arrows
        self.create_table(0, 0, rows, cols)  # TODO: replace x and  with table position

        # self.setup_background(rows, cols, cell_width, cell_height)

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

    def create_table(self, x, y, x_times, y_times):
        for i in range(x_times):
            self._positions.append([])
            for j in range(y_times):
                null_arrow = False
                center_x = x + self.x_spacing * i + (self.hex_size * 0.9 if j % 2 == 0 else 0) + self.spacing
                center_y = y + self.y_spacing * j + self.spacing
                self._positions[i].append([center_x, center_y])

                hexagon = QGraphicsPolygonItem(self.create_hexagon(center_x, center_y))
                hexagon.setPen(self.pen)
                hexagon.setBrush(self.brush)
                self.addToGroup(hexagon)

                # Displaying the vector
                if self.angle_field is not None:
                    t = self.angle_field[i][j]
                    if t[0] is None:
                        continue
                    else:
                        vector = np.array(t[1])
                        angle_rad = np.arccos(
                            np.dot(vector, [1, 0]) / (np.linalg.norm(vector) * np.linalg.norm([1, 0])))
                        # radians to degrees
                        angle_deg = np.degrees(angle_rad)
                        self.vector_dir = angle_rad  # math.atan2(*t[1])
                # convert self.vector_dir to an angle
                vec_x_end = center_x + self.vector_length * cos(self.vector_dir)
                vec_y_end = center_y + self.vector_length * sin(self.vector_dir)
                line = QGraphicsLineItem(center_x, center_y, vec_x_end, vec_y_end)
                line.setPen(self.vector_pen)

                arrow_angle = self.vector_dir + math.pi * (3 / 4)
                arrow_right = QGraphicsLineItem(vec_x_end, vec_y_end,
                                                vec_x_end + ((self.vector_length / 2) * cos(arrow_angle)),
                                                vec_y_end + ((self.vector_length / 2) * sin(arrow_angle)))
                arrow_angle -= math.pi * (3 / 4) * 2
                arrow_left = QGraphicsLineItem(vec_x_end, vec_y_end,
                                               vec_x_end + ((self.vector_length / 2) * cos(arrow_angle)),
                                               vec_y_end + ((self.vector_length / 2) * sin(arrow_angle)))

                arrow_left.setPen(self.vector_pen)
                arrow_right.setPen(self.vector_pen)

                if self.show_arrows and not null_arrow:
                    self.addToGroup(line)
                    self.addToGroup(arrow_right)
                    self.addToGroup(arrow_left)
        print("All positions: ", self.positions)


class Table_preview(QWidget):
    json_vec_field_filename = r'C:\Users\toupa\Desktop\ESE - S1\PFE\3D\New folder\controllers\dataexchange.pkl'

    def __init__(self, *args):
        super().__init__(*args)
        self.drag_rectangle = None
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._package_size = 20
        self.show_arrows = False
        self.angle_field = None
        self._package_size = 10

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

    def save_vec_field_data(self):
        # TODO: This only saves one list at a time, fix later
        t = self.numpy_array_to_list(self.angle_field)
        print('angle field: ', t)
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
        self.update_background_scene() # TODO: Create option not to delete rects + lines
        self.save_vec_field_data()


        self.scene.addItem(self.background_item)
        self.view.setScene(self.scene)

    def create_vector_field(self, path_points, vec_fiel, x, y):
        vector_field = [[0 for j in range(y)] for i in range(x)]
        for i in range(len(vec_fiel)):
            for j in range(len(vec_fiel[0])):
                cell = vec_fiel[i][j]
                # find all the points close to tolerance
                # closest_point = path_points[indices_list[0]]

                # vector_field[i][j] = tangents[indices_list[0]]
                # vector_field[i][j] = self.get_smoothed_direction(path_points, indices_list[0], 60)
                # t = self.get_local_regression_direction(path_points, indices_list[0], 60, 1)
                # print("The result of local regression is: ", t)
                # vector_field[i][j] = t
                vector_field[i][j] = self.get_distance_and_tangent(cell, path_points, self._package_size)

        return vector_field

    @staticmethod
    def is_close_to_path(cell_center, path_points, threshold_distance):
        # threshold distance is the distance from the center of the cell center constraint by the size of the package
        distances = []
        for p in path_points:
            distances.append(sq(abs((cell_center[0] - p[0]) ** 2 + (cell_center[1] - p[1]) ** 2)))
        dist = []
        for d in range(len(distances)):
            if distances[d] < threshold_distance:
                dist.append(d)
        dist.sort(key=lambda x: distances[x])
        return dist

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
            return min_distance, closest_tangent / magnitude
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
        print("*************************************")
        print("Value of angle_field:", self.angle_field)
        print("*************************************")
        self.background_item = BackgroundItem(self.scene, self.table_rows, self.table_cols, cell_width, cell_height,
                                              self.show_arrows, self.angle_field)
        self.scene.clear()
        self.scene.addItem(self.background_item)
        self.view.setScene(self.scene)

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
            self.timer = QTimer(self)
            self.timer.setInterval(100)  # Call every 100 milliseconds
            self.timer.timeout.connect(self.update_and_draw_rectangle)
            self.timer.start()
            self.coor_list.append([])
            print("Starting to record a new list...")

            # square is stuck to mouse, placed when clicked, won't stop until clicking on waypoint button or ESC key
        else:
            # stop placing waypoints and expect a list of waypoints
            self.timer.stop()
            print("Now list recorded. showing: ", self.coor_list[self.coor_index])
            self.drawing = False
            self.last_point = None
            self.coor_index += 1

    def mousePressEvent(self, event):
        # TODO: draw a phantom line between two squares
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

    def get_cursor_position_in_view(self):
        # cursor_pos = win32api.GetCursorPos()
        # viewport_pos = self.view.viewport().mapToGlobal(QPoint(0, 0))
        # view_relative_pos = QPoint(cursor_pos[0] + viewport_pos.x(), cursor_pos[1] + viewport_pos.y())
        # pos = QCursor.pos()  #viewport().mapFromGlobal | mapToScene
        # pos_2 = self.view.viewport().mapFromGlobal(QCursor.pos())  #viewport().mapFromGlobal | mapToScene

        pos = self.view.viewport().mapFromGlobal(QCursor.pos())  # Get viewport that is GraphicView
        scene_pos = self.view.mapToScene(pos)  # Get scene coordinates, with respect to scrolling and same plane as hex
        return scene_pos

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
        print("Rect at: ", cursor_pos.x(), cursor_pos.y())

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

    def set_package_size(self, val):
        self._package_size = val


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
        lay = QVBoxLayout(self.content_widget)  # main layout
        # box size spin box
        self.package_size_spin_box = QSpinBox()
        self.package_size_spin_box.setMinimum(10)
        self.package_size_spin_box.setValue(60)
        self.package_size_spin_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

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
        lay.addWidget(self.package_size_spin_box)
        lay.addWidget(self.waypoint_pins)
        lay.addWidget(self.pick_wayp_list)  # TODO: connect indexChanged to model listview different self.coor_list
        lay.addWidget(self.list_view)

        self.layout.addWidget(self.content_widget)

    def insert_item_to_list(self, item):
        self.model.appendRow(QStandardItemModel(item))

    def toggle_collapse(self):
        if self.is_collapsed:
            # self._expand_animation()
            self.content_widget.show()
            self.setMaximumWidth(400)  # TODO: width too big, change after adding all widget to something smaller
            self.setMinimumWidth(400)
            self.header_label.setText(">")
        else:
            # self._collapse_animation()
            self.content_widget.hide()
            self.setMaximumWidth(50)
            self.setMinimumWidth(50)
            self.header_label.setText("<")
        self.is_collapsed = not self.is_collapsed

    def _collapse_animation(self):
        print(f"_collapse_animation, width: {self.content_widget.width()}")
        animation = QPropertyAnimation(self.content_widget, b"minimumWidth")
        animation.setDuration(250)
        animation.setStartValue(self.content_widget.width())
        animation.setEndValue(50)
        animation.setEasingCurve(QEasingCurve.Linear)
        animation.finished.connect(lambda: self.content_widget.hide())
        animation.start()

    def _expand_animation(self):
        print(f"_expand_animation, width: {self.content_widget.width()}")
        animation = QPropertyAnimation(self.content_widget, b"minimumWidth")
        animation.setDuration(250)
        animation.setStartValue(0)
        animation.setEndValue(self.content_widget.width())
        animation.setEasingCurve(QEasingCurve.Linear)
        animation.finished.connect(lambda: self.content_widget.show())
        animation.start()


class MainUi(QMainWindow):
    def __init__(self, robot: Robot):
        super(MainUi, self).__init__()
        ui_filename = r'C:\Users\toupa\Desktop\ESE - S1\PFE\Simulation_files\ui_files\window_0_1.ui'
        loadUi(ui_filename, self)
        self.resize(1366, 768)
        self.robot = robot
        self._default_values = self.robot.default_values
        self.show_arrows = False
        self.stackedWidget_3000: QStackedWidget = self.findChild(QStackedWidget, "stackedWidget_3000")
        self.stackedWidget_3000.setCurrentIndex(1)
        self.table_preview = self.findChild(QWidget, 'show_table')
        self.table_preview_2 = self.findChild(QWidget, 'table_draw_enabled')
        self.foldable_toolbar = self.findChild(QWidget, 'FoldableToolBar')

        self.initialize()

    def initialize(self):
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
        self.create_progressBar:QProgressBar = self.findChild(QProgressBar, "create_progressBar")
        self.create_progressBar.setValue(0)
        self.button_create.clicked.connect(self.create_webot_world_file)
        self.dimension_x.valueChanged.connect(self.update_table_preview)
        self.dimension_y.valueChanged.connect(self.update_table_preview)
        self.foldable_toolbar.package_size_spin_box.valueChanged.connect(
            lambda: self.table_preview_2.change_pen_size(self.foldable_toolbar.package_size_spin_box.value()))
        self.foldable_toolbar.waypoint_pins.clicked.connect(lambda: self.table_preview_2.mouse_hover(
            self.foldable_toolbar.waypoint_pins))

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
        print("Creating file ...")
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
        print("File created.")

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
        self.calculate_button = self.findChild(QPushButton, 'calculate_button')
        self.launch_button = self.findChild(QPushButton, 'launch_button')

        self.launch_button.clicked.connect(lambda: self.robot.start_controller(0, 0, 1))  # TODO: redo
        # elipse = self.scene.addEllipse(20, 20, 200, 200, self.pen, self.brush_blue)
        # poly = QPolygonF()
        # poly = self.get_hexagon(0, 0, 20)

        # self.scene.addPolygon(poly, self.pen, self.brush_blue)
        # self.update_table_preview()
        pass

    @property
    def default_values(self):
        return self._default_values


if __name__ == '__main__':
    app = QApplication(sys.argv)
    r = Robot(translation=[0, 0, 0.1], dimensions=[5, 5], rotation=[0, 0, 1, 0], controller=r'<extern>')
    ui = MainUi(r)
    ui.show()
    app.exec_()
