import uuid

from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QSizePolicy, QListView, QHBoxLayout, QVBoxLayout, QPushButton, QTabWidget, \
    QSpinBox, QComboBox, QLabel, QListView, QLineEdit


class LaneGraphicRepresentation:
    def __init__(self, i: int, j: int, direction_str: str, position_in_gui: list, count_for_name: int):
        self._i = i
        self._j = j
        self.direction_str = direction_str
        self._position = position_in_gui
        self._name = f'{self.direction_str} {count_for_name}'

    @property
    def position(self):
        return self._position

    @property
    def name(self):
        return self._name

    @property
    def coordinates(self):
        return self._i, self._j

    @property
    def i(self):
        return self._i

    @i.setter
    def i(self, value):
        self._i = value

    @property
    def j(self):
        return self._j

    @j.setter
    def j(self, value):
        self._j = value

    def __str__(self):
        return f"Lane named: {self._name} adjacent to cell [{self.i}, {self.j}]"


class Package:
    def __init__(self, package_size: int, starting_order: int, starting_lane: LaneGraphicRepresentation,
                 ending_lane: LaneGraphicRepresentation,
                 unique_id: int = None):
        if unique_id is None:
            self._unique_id = uuid.uuid4()
        else:
            self.unique_id = unique_id
        self._package_size = package_size
        self.starting_lane = starting_lane
        self.ending_lane = ending_lane
        self._starting_orde = starting_order

    def item_display(self):
        return f"Starting lane: {self.starting_lane.name}\nEnding lane: {self.ending_lane.name}\nPackage size: {self._package_size}\nOrder: {self._starting_orde}\n"

    def __lt__(self, other):
        if isinstance(other, Package):
            return self._starting_order < other._starting_order
        else:
            raise TypeError("Comparison with non-Package types is not supported.")


class FoldableToolBar(QWidget):
    def __init__(self, parent=None):
        super(FoldableToolBar, self).__init__(parent)
        self.package_size_spin_box = None
        self.setObjectName("FoldableToolBar")
        self.is_collapsed = False
        self._lane_representation_list: list[LaneGraphicRepresentation] = []

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

        self._package_queue = []
        self._waypoints_count = 0
        self._waypoints_models = []
        self.active_model = None
        self.set_content()

    def set_content(self):
        self.tab = QTabWidget()
        self.tab.setObjectName("Edit_area_tab")
        self.tab_manual = QWidget()
        self.tab_auto = QWidget()
        package_list = QWidget()
        self.tab.addTab(self.tab_manual, "Manual")
        self.tab.addTab(self.tab_auto, "Automatic")
        self.tab.addTab(package_list, "Packages")

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
        self.waypoint_pins.clicked.connect(self.record_waypoints)

        self.pick_wayp_list = QComboBox()
        self.pick_wayp_list.currentIndexChanged.connect(self.switch_pick_way)

        self.list_view = QListView()
        self.model = QStandardItemModel()  # TODO: Create a signal to know when a box has been created to insert to listview
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
        self.current_angle = QLabel("Angle: Table OFF")
        self.current_angle.setFixedWidth(200)
        self.current_angle.setFixedHeight(50)
        #lay_a.addWidget(self.auto_spin_box_label_widget)
        lay_a.addWidget(self.auto_button_w)
        lay_a.addWidget(self.automatic_paths)
        lay_a.addWidget(self.current_angle)
        lay_a.addWidget(self.automatic_list)

        # package tab
        package_lay = QVBoxLayout(package_list)
        package_list_view = QListView()
        self.package_list_model = QStandardItemModel()
        add_package_button_w = QWidget()
        add_package_button_lay = QVBoxLayout()
        # add order
        wig_order = QWidget()
        lay_order = QHBoxLayout(wig_order)
        label_order = QLabel("Order: ")
        self.input_order = QLineEdit()
        lay_order.addWidget(label_order)
        lay_order.addWidget(self.input_order)
        lay_order.setSpacing(0)
        lay_order.setContentsMargins(0, 0, 0, 0)

        wig_size = QWidget()
        lay_size = QHBoxLayout(wig_size)
        label_size = QLabel("Package size: ")
        self.input_size = QLineEdit()
        lay_size.addWidget(label_size)
        lay_size.addWidget(self.input_size)
        lay_size.setSpacing(0)
        lay_size.setContentsMargins(0, 0, 0, 0)

        wig_lane = QWidget()
        lay_lane = QHBoxLayout(wig_lane)
        label_lane = QLabel("Starting lane: ")
        self.input_lane = QComboBox()
        lay_lane.addWidget(label_lane)
        lay_lane.addWidget(self.input_lane)
        lay_lane.setSpacing(0)
        lay_lane.setContentsMargins(0, 0, 0, 0)

        wig_lane_end = QWidget()
        lay_lane_end = QHBoxLayout(wig_lane_end)
        label_lane_end = QLabel("Ending lane: ")
        self.output_lane = QComboBox()
        lay_lane_end.addWidget(label_lane_end)
        lay_lane_end.addWidget(self.output_lane)
        lay_lane_end.setSpacing(0)
        lay_lane_end.setContentsMargins(0, 0, 0, 0)

        self.add_package_to_queue_button = QPushButton("Add")
        self.add_package_to_queue_button.clicked.connect(self.add_package_to_queue)

        add_package_button_lay.addWidget(wig_order)
        add_package_button_lay.addWidget(wig_size)
        add_package_button_lay.addWidget(wig_lane)
        add_package_button_lay.addWidget(wig_lane_end)
        add_package_button_lay.addWidget(self.add_package_to_queue_button)

        package_list_view.setModel(self.package_list_model)
        package_list_view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        add_package_button_w.setLayout(add_package_button_lay)
        add_package_button_w.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        add_package_button_lay.setSpacing(0)
        add_package_button_lay.setContentsMargins(0, 0, 0, 0)
        package_lay.addWidget(package_list_view)
        package_lay.addWidget(add_package_button_w)
        self.layout.addWidget(self.tab)

    @property
    def manual_list_view(self):
        return self.active_model

    def record_waypoints(self):
        if not self.waypoint_pins.isChecked():
            return
        self._waypoints_models.append(QStandardItemModel())
        self.pick_wayp_list.addItem(f'Waypoint - {self._waypoints_count+1}')
        self.pick_wayp_list.setCurrentIndex(self.pick_wayp_list.count()-1)
        self._waypoints_count += 1

    def switch_pick_way(self):
        t = self.objectName()
        index = self.pick_wayp_list.currentIndex()
        self.active_model = self._waypoints_models[index]
        self.list_view.setModel(self.active_model)

    def insert_item_to_list(self, item, manual=True, path=False):
        if manual and not path:
            self.model.appendRow(QStandardItemModel(item))
        elif not manual and not path:
            self.automatic_model.appendRow(QStandardItemModel(item))
        elif manual and path:
            self.pick_wayp_list.addItem(item)
        elif not manual and path:
            self.automatic_paths.addItem(item)

    def add_package_to_queue(self):
        order = self.input_order.text()
        psize = self.input_size.text()
        lane = self.input_lane.currentText()
        lane_end = self.output_lane.currentText()

        self.input_order.clear()
        self.input_size.clear()
        self.input_lane.clear()
        self.output_lane.clear()
        starting_lane, ending_lane = None, None
        for lane_rep in self._lane_representation_list:
            if lane_rep.name.lower() == lane.lower():
                starting_lane = lane_rep
            if lane_rep.name.lower() == lane_end.lower():
                ending_lane = lane_rep

        item = Package(package_size=psize, starting_order=order, starting_lane=starting_lane, ending_lane=ending_lane)
        self._package_queue.append(item)

        t = QStandardItem(item.item_display())
        self.package_list_model.appendRow(t)

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

    @property
    def lane_representation_list(self):
        return self._lane_representation_list

    @lane_representation_list.setter
    def lane_representation_list(self, value):
        self._lane_representation_list = value

    @property
    def package_queue(self):
        return self._package_queue

    @package_queue.setter
    def package_queue(self, val: list):
        self._package_queue = val
