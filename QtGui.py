import math
from math import cos, sin, radians
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow
import sys
from WBWorldGenerator import Robot
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsView, QVBoxLayout, QWidget, QPushButton, QSpinBox, \
    QLabel, QGraphicsLineItem, QHBoxLayout, QGraphicsRectItem, QFileDialog, QStackedWidget, QGraphicsPolygonItem, QGraphicsItemGroup
from PyQt5.QtGui import QBrush, QPen, QPolygonF, QPainter, QImage, QPixmap, QPainterPath, QColor
from PyQt5.QtCore import Qt, QPointF, QLineF, QEvent, QRectF, pyqtSlot


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

    def create_table(self, x, y, x_times, y_times):
        for i in range(x_times):
            for j in range(y_times):
                center_x = x + self.x_spacing * i + (self.hex_size * 0.9 if j % 2 == 0 else 0) + self.spacing
                center_y = y + self.y_spacing * j + self.spacing

                hexagon = QGraphicsPolygonItem(self.create_hexagon(center_x, center_y))
                hexagon.setPen(self.pen)
                hexagon.setBrush(self.brush)
                if self.angle_field:
                    self.vector_dir = self.angle_field[i][j]
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
            self.scene.addPath(p, pen)
        print("coordinates list: ", self.coor_list)
        self.angle_field = self.get_vec_field_from_path(0)   # TODO: add list to choose from in QAction menu

        self.scene.addItem(self.background_item)
        self.view.setScene(self.scene)

    def get_vec_field_from_path(self, index):
        points = []
        print("Using path number: ", self.coor_index - 1)
        for qp in self.coor_list[self.coor_index-1]:
            points.append((qp.x(), qp.y()))
        # TODO: Fix the hexagon cell width, height and dist between
        self.hex_size = 40  # Size of hexagons
        self.spacing = -100  # Spacing between hexagons
        self.x_spacing = self.hex_size * 1.7
        self.y_spacing = self.hex_size * 1.5
        self.vector_length = self.hex_size / 2
        angle_field = [[0 for i in range(self.table_cols)] for j in range(self.table_rows)]
        for i in range(self.table_rows):
            for j in range(self.table_cols):
                center_x = self.x_spacing * i + (self.hex_size * 0.9 if j % 2 == 0 else 0) + self.spacing
                center_y = self.y_spacing * j + self.spacing

                vector_position = (center_x, center_y)
                closest_point = min(points, key=lambda p: math.dist(p, vector_position))

                # Calculate the direction vector from the current vector to the closest point on the path
                direction_vector = (closest_point[0] - vector_position[0], closest_point[1] - vector_position[1])
                direction_length = math.sqrt(direction_vector[0] ** 2 + direction_vector[1] ** 2)
                direction_vector = (direction_vector[0] / direction_length, direction_vector[1] / direction_length)

                angle = math.atan2(direction_vector[1], direction_vector[0])
                angle_field[i][j] = angle
        return angle_field

    def launch_controller(self):
        self.main_window.robot.launch_controller_string(1, 1, 0)
        pass

    def setup_background_scene(self):  # TODO: implement to be called from MainUi using dimension_x inputs
        cell_width = 50
        cell_height = 50
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
                if self.last_point is not None:
                    self.draw_on_scene(self.last_point, current_point)
                    print(" compare: ", self.coor_index, " with ", len(self.coor_list))
                    self.coor_list[self.coor_index].append(current_point)
                self.last_point = current_point
        elif event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.drawing = True
                self.last_point = self.view.mapToScene(event.pos())
                self.coor_list.append([event.pos()])
        elif event.type() == QEvent.MouseButtonRelease:
            self.coor_index += 1
            self.path_index += 1
            self.paths.append([])
            if event.button() == Qt.LeftButton:
                self.drawing = False
                self.last_point = None
        return super().eventFilter(obj, event)

    def draw_on_scene(self, start_point, end_point):
        # Draw on the foreground scene
        pen = QPen(Qt.red, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
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
