import math
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow
import sys
from WBWorldGenerator import Robot
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem
from PyQt5.QtGui import QBrush, QPen, QPolygonF, QPainter
from PyQt5.QtCore import Qt, QPointF


class tale_preview(QGraphicsScene):
    def __init__(self, *args):
        super().__init__(*args)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        self.pen = QPen(Qt.black, 2)
        self.last_point = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()
            self.draw_point(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.draw_line(self.last_point, event.pos())
            self.last_point = event.pos()

    def draw_point(self, point):
        self.scene.addEllipse(point.x() - 1, point.y() - 1, 2, 2, self.pen)

    def draw_line(self, start_point, end_point):
        self.scene.addLine(start_point.x(), start_point.y(), end_point.x(), end_point.y(), self.pen)


class MainUi(QMainWindow):
    def __init__(self, robot: Robot):
        super(MainUi, self).__init__()
        ui_filename = r'C:\Users\toupa\Desktop\ESE - S1\PFE\Simulation_files\ui_files\window_0_1.ui'
        loadUi(ui_filename, self)
        self.robot = robot
        self.initialize()

    def initialize(self):

        self.set_triggers()
        self.set_default_values()
        self.set_table_preview()

    def set_triggers(self):
        self.button_create.clicked.connect(self.create_webot_world_file)
        self.dimension_x.valueChanged.connect(self.update_table_preview)
        self.dimension_y.valueChanged.connect(self.update_table_preview)

    def update_table_preview(self):
        raduis = 20
        self.scene = QGraphicsScene()
        self.brush_blue = QBrush(Qt.blue)
        self.pen = QPen()
        self.set_and_get_polygon_crystal(self.dimension_x.value(), self.dimension_y.value(), self.scene, 0, 0, raduis)
        self.Table_preview.setScene(self.scene)

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



        # elipse = self.scene.addEllipse(20, 20, 200, 200, self.pen, self.brush_blue)
        #poly = QPolygonF()
        #poly = self.get_hexagon(0, 0, 20)

        #self.scene.addPolygon(poly, self.pen, self.brush_blue)
        #self.update_table_preview()
        pass

    def set_and_get_polygon_crystal(self, dimension_x, dimension_y, scene: QGraphicsScene,
                            left_bottom_cell_center_coordinates_x,
                            left_bottom_cell_center_coordinates_y, cell_radius):

        # TODO:use left_bottom ..... for translating scene into the middle
        # TODO:unite the coordinates system between the two or create a conversion function
        polies = []
        dist_between_cells = cell_radius * 1.7
        x_offset = 100
        y_offset = 0
        #(cell_radius / 2)  # TODO: If the cells are too far off, this is at fault because it's
        # supposed to be cell_radius*cos(60) but I want some extra distance
        t = - 1
        for j in range(dimension_y):
            y = dist_between_cells * j + y_offset
            t *= -1
            for i in range(dimension_x):
                if j % 2 == 0:
                    x = dist_between_cells * i + x_offset
                else:
                    x = (dist_between_cells * i) + (t * dist_between_cells / 2) + x_offset
                polies.append(self.get_hexagon(x, y, cell_radius))

        for p in polies:
            scene.addPolygon(p, self.pen, self.brush_blue)  # TODO: best place to reconsider styling
        return polies

    @staticmethod
    def get_hexagon(center_x, center_y, radius):
        vertices = []
        angle_deg = 60
        angle_deg_offset = 30
        ans = QPolygonF()
        for i in range(6):
            angle_rad = math.radians(angle_deg * i + angle_deg_offset)
            x = center_x + radius * math.cos(angle_rad)
            y = center_y + radius * math.sin(angle_rad)
            vertices.append((x, y))
        for p in vertices:
            ans << QPointF(p[0], p[1])

        return ans


if __name__ == '__main__':
    app = QApplication(sys.argv)
    r = Robot(translation=[0, 0, 0.1], dimensions=[5, 5], rotation=[0, 0, 1, 0], controller=r'<extern>')
    ui = MainUi(r)
    ui.show()
    app.exec_()
