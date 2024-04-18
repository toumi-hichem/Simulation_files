import math
#import statsmodels.api as sm
from math import cos, sin, radians
from math import sqrt as sq
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow
import sys
from WBWorldGenerator import Robot
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsView, QVBoxLayout, QWidget, QPushButton, QSpinBox, \
    QLabel, QGraphicsLineItem, QHBoxLayout, QGraphicsRectItem, QFileDialog, QStackedWidget, QGraphicsPolygonItem, QGraphicsItemGroup
from PyQt5.QtGui import QBrush, QPen, QPolygonF, QPainter, QImage, QPixmap, QPainterPath, QColor
from PyQt5.QtCore import Qt, QPointF, QLineF, QEvent, QRectF, pyqtSlot


# TODO: Create a side tab which varies the mouse painter size to accomodate different package sizes
# maybe even exclude individual engines if not inside bounds to save energy

def get_hexagon(x, y, length):
    starting_angle = 30
    angle_between = 60
    poly = QPolygonF()

    for i in range(6):

        poly << QPointF(cos(radians(starting_angle + angle_between * i)), sin(radians(starting_angle + angle_between * i)))
    return poly


class BackgroundItem(QGraphicsItemGroup):    # QGraphicsPolygonItem
    def __init__(self, scene, rows, cols, cell_width, cell_height, show_arrows, angle_field=None):
        super().__init__()
        #0, 0, cols * cell_width, rows * cell_height
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

                center_x = x + self.x_spacing * i + (self.hex_size * 0.9 if j % 2 == 0 else 0) + self.spacing
                center_y = y + self.y_spacing * j + self.spacing
                self._positions[i].append([center_x, center_y])

                hexagon = QGraphicsPolygonItem(self.create_hexagon(center_x, center_y))
                hexagon.setPen(self.pen)
                hexagon.setBrush(self.brush)
                if self.angle_field is not None:
                    self.vector_dir = math.atan2(*self.angle_field[i][j])
                # convert self.vector_dir to an angle

                vec_x_end = center_x + self.vector_length * cos(self.vector_dir)
                vec_y_end = center_y + self.vector_length * sin(self.vector_dir)
                line = QGraphicsLineItem(center_x, center_y, vec_x_end, vec_y_end)
                line.setPen(self.vector_pen)

                arrow_angle = self.vector_dir + math.pi * (3 / 4)
                arrow_right = QGraphicsLineItem(vec_x_end, vec_y_end, vec_x_end + ((self.vector_length / 2) * cos(arrow_angle)), vec_y_end + ((self.vector_length / 2) * sin(arrow_angle)))
                arrow_angle -= math.pi * (3 / 4) * 2
                arrow_left  = QGraphicsLineItem(vec_x_end, vec_y_end, vec_x_end + ((self.vector_length / 2) * cos(arrow_angle)), vec_y_end + ((self.vector_length / 2) * sin(arrow_angle)))

                arrow_left.setPen(self.vector_pen)
                arrow_right.setPen(self.vector_pen)

                self.addToGroup(hexagon)

                if self.show_arrows:
                    self.addToGroup(line)
                    self.addToGroup(arrow_right)
                    self.addToGroup(arrow_left)
        print("All positions: ", self.positions)

class Table_preview(QWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.show_arrows = False
        self.angle_field = None
        self.parent = self.parent()
        self.parent.objectName()
        self.background_item = None
        self.view = QGraphicsView()
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
        # Install event filter to capture mouse move events

        # Variables to track drawing
        self.last_point = None
        self.drawing = False

    def setup_buttons(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout_button = QHBoxLayout()
        button_widget = QWidget()

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
            pass    # do not any but the preview, no drawing, too.
        elif self.parent.objectName() == 'edit_mode':
            self.view.viewport().installEventFilter(self)
            layout.addWidget(button_widget)
        self.setLayout(layout)

    def calculate_path(self):
        pen = QPen(Qt.red, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        for p in self.paths[self.path_index - 1]:
            self.scene.addPath(p, pen)        #self.angle_field = self.get_vec_field_from_path(0)   # TODO: add list to choose from in QAction menu
        points = self.coor_list[self.coor_index-1]
        vec_fiel = self.background_item.positions
        # TODO: Add threshold to gui
        self.angle_field = self.create_vector_field(points, vec_fiel, 5, 5, 90)
        self.update_background_scene()

        self.scene.addItem(self.background_item)
        self.view.setScene(self.scene)

    def get_vec_field_from_path(self, index):
        points = []
        print("Using path number: ", self.coor_index - 1)
        #for qp in self.coor_list[self.coor_index-1]:
        #    points.append((qp.x(), qp.y()))
        points = self.coor_list[self.coor_index-1]
        # TODO: Fix the hexagon cell width, height and dist between
        self.hex_size = 40  # Size of hexagons
        self.spacing = -100  # Spacing between hexagons
        self.x_spacing = self.hex_size * 1.7
        self.y_spacing = self.hex_size * 1.5
        self.vector_length = self.hex_size / 2
        tolerance = 40
        angle_field = [[0 for i in range(self.table_cols)] for j in range(self.table_rows)]
        i, j = 0, 0
        for cell in points:
            cell_center = cell
            # Check if the cell is close enough to the path
            if self.is_cell_close_to_path(cell_center, tolerance):
                # Calculate the tangent direction at the nearest point on the path
                tangent_vector = self.calculate_tangent_at_nearest_point(cell_center)
                self.angle_field.append

    @staticmethod
    def get_smoothed_direction(path, point_index, window_size):
        """
        Estimates the direction at a point using moving average and finite differencing.

        Args:
            path: A list of coordinates representing the path points.
            point_index: The index of the point in the path for which to estimate the direction.
            window_size: The size of the moving average window.

        Returns:
            A list representing the estimated direction vector.
        """

        if window_size % 2 == 0:
            window_size += 1

        half_window = window_size // 2  # Integer division for window center
        smoothed_x = 0
        smoothed_y = 0

        # Calculate moving average centered on the point
        for i in range(point_index - half_window, point_index + half_window + 1):
            if 0 <= i < len(path):
                smoothed_x += path[i][0]
                smoothed_y += path[i][1]

        smoothed_x /= window_size
        smoothed_y /= window_size

        # Estimate direction using previous or next point (depending on edge cases)
        if point_index == 0:
            return [smoothed_x - path[point_index + 1][0], smoothed_y - path[point_index + 1][1]]
        elif point_index == len(path) - 1:
            return [path[point_index - 1][0] - smoothed_x, path[point_index - 1][1] - smoothed_y]
        else:
            return [smoothed_x - path[point_index - 1][0], smoothed_y - path[point_index - 1][1]]

    @staticmethod
    def get_estimated_tangent(path, point_index):
        """
        Estimates the tangent vector at a point in the path using finite differencing.

        Args:
            path: A list of coordinates representing the path points.
            point_index: The index of the point in the path for which to estimate the tangent vector.

        Returns:
            A list representing the estimated tangent vector.
        """

        if point_index == 0:
            # Handle edge case for first point (use next two points)
            delta_x = path[point_index + 1][0] - path[point_index][0]
            delta_y = path[point_index + 1][1] - path[point_index][1]
        elif point_index == len(path) - 1:
            # Handle edge case for last point (use previous two points)
            delta_x = path[point_index][0] - path[point_index - 1][0]
            delta_y = path[point_index][1] - path[point_index - 1][1]
        else:
            # Estimate tangent for middle points
            delta_x = path[point_index + 1][0] - path[point_index - 1][0]
            delta_y = path[point_index + 1][1] - path[point_index - 1][1]

        # Calculate magnitude (avoid division by zero)
        magnitude = (delta_x ** 2 + delta_y ** 2) ** 0.5
        if magnitude > 0:
            # Normalize to get unit tangent vector
            return [delta_x / magnitude, delta_y / magnitude]
        else:
            # Handle case of zero vector (consider stopping or adjusting path)
            return [0, 0]

    @staticmethod
    def get_local_regression_direction(path, point_index, window_size, degree):
        """
        Estimates the direction at a point using local regression (scikit-learn).

        Args:
            path: A list of coordinates representing the path points.
            point_index: The index of the point in the path for which to estimate the direction.
            window_size: The size of the window for local regression.
            degree: The degree of the polynomial to fit for loess.

        Returns:
            A list representing the estimated direction vector (slope).
        """

        # Extract x and y coordinates
        x = [[point[0]] for point in path]  # Reshape for scikit-learn format
        y = [point[1] for point in path]

        # Define model with desired parameters
        model = LocalPolynomialRegression(degree=degree, n_neighbors=window_size)

        # Fit the model on the path data
        model.fit(x, y)

        # Predict the fitted y value for the current point
        predicted_y = model.predict([[x[point_index][0]]])[0]

        # Estimate direction based on slope (difference in y)
        if point_index == 0:
            return [0, predicted_y - y[point_index + 1]]  # Handle edge case (use next point)
        elif point_index == len(path) - 1:
            return [0, predicted_y - y[point_index - 1]]

    def create_vector_field(self, path_points, vec_fiel, x, y, threshold_distance):
        vector_field = [[0 for j in range(y)] for i in range(x)]
        for i in range(len(vec_fiel)):
            for j in range(len(vec_fiel[0])):
                cell = vec_fiel[i][j]
                # find all the points close to tolerance
                indices_list = self.is_close_to_path(cell, path_points, threshold_distance)
                #closest_point = path_points[indices_list[0]]
                if indices_list:
                    #vector_field[i][j] = tangents[indices_list[0]]
                    vector_field[i][j] = self.get_smoothed_direction(path_points, indices_list[0], 60)
                    #t = self.get_local_regression_direction(path_points, indices_list[0], 60, 1)
                    #print("The result of local regression is: ", t)
                    #vector_field[i][j] = t
                else:
                    vector_field[i][j] = [0, 0]
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

    def launch_controller(self):
        self.main_window.robot.launch_controller_string(1, 1, 0)
        pass

    def setup_background_scene(self):  # TODO: implement to be called from MainUi using dimension_x inputs
        cell_width = 50
        cell_height = 50
        print("*************************************")
        print("Value of angle_field:", self.angle_field)
        print("*************************************")
        self.background_item = BackgroundItem(self.scene, self.table_rows, self.table_cols, cell_width, cell_height, self.show_arrows, self.angle_field)
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

    def eventFilter(self, obj, event):
        # Filter mouse move events
        if event.type() == QEvent.MouseMove:
            if self.drawing:
                current_point = self.view.mapToScene(event.pos())
                try:
                    self.coor_list[self.coor_index].append([current_point.x(), current_point.y()])
                except IndexError:
                    self.coor_index -= 1
                    self.coor_list[self.coor_index].append([current_point.x(), current_point.y()])
                if self.last_point is not None:
                    self.draw_on_scene(self.last_point, current_point)

                self.last_point = current_point
        elif event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.drawing = True
                self.last_point = self.view.mapToScene(event.pos())
                self.coor_list.append([[self.last_point.x(), self.last_point.y()], ])
        elif event.type() == QEvent.MouseButtonRelease:
            self.coor_index += 1
            self.path_index += 1
            self.paths.append([])
            if event.button() == Qt.LeftButton:
                self.drawing = False
                self.last_point = None
        return super().eventFilter(obj, event)

    def draw_on_scene(self, start_point, end_point):
        self.pen_size = 20
        # Draw on the foreground scene
        pen = QPen(Qt.red, self.pen_size, Qt.DotLine, Qt.RoundCap, Qt.RoundJoin)
        path = QPainterPath()
        path.moveTo(start_point)
        path.lineTo(end_point)
        self.scene.addPath(path, pen)
        self.paths[self.path_index].append(path)
        self.scene.addItem(self.background_item)
        self.view.setScene(self.scene)


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
        self.table_preview = self.findChild(QWidget, 'widget')
        self.table_preview_2 = self.findChild(QWidget, 'widget_2')

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
        self.actionPath_and_preview.triggered.connect(lambda: self.switch_menu(self.actionPath_and_preview))    # 0

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
        self.button_create.clicked.connect(self.create_webot_world_file)
        self.dimension_x.valueChanged.connect(self.update_table_preview)
        self.dimension_y.valueChanged.connect(self.update_table_preview)

    def update_table_preview(self):  # TODO: deprecated, remove later
        raduis = 20
        self.scene = QGraphicsScene()
        self.brush_blue = QBrush(Qt.blue)
        self.pen = QPen()
        self.table_preview.set_background_parameters(self.dimension_x.value(), self.dimension_y.value(), self.show_arrows)
        self.table_preview_2.set_background_parameters(self.dimension_x.value(), self.dimension_y.value(), self.show_arrows)
        # self.Table_preview.setScene(self.scene)

    def create_webot_world_file(self):
        # TODO: connect clicking the button with extracting all the values from the UI
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

        self.launch_button.clicked.connect(lambda: self.robot.start_controller(0, 0, 1)) # TODO: redo
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
