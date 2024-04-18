import os, subprocess, asyncio, platform


class SFVec:
    # TODO: sfvec to sfvec assignment, same for SFString
    def __init__(self, val):
        self.val = val

    def __str__(self):
        self.val_str = ''
        if isinstance(self.val, list):
            for i in self.val:
                if isinstance(i, str):
                    self.val_str += f'"{i}"' + " "
                else:
                    self.val_str += str(i) + " "
            self.val_str += ''
        return self.val_str

    def __getitem__(self, item):
        assert isinstance(item, int)
        return self.val[item]

    def get_coordinates(self):
        return self.val

    @property
    def x(self):
        return self.val[0]

    @property
    def y(self):
        return self.val[1]

    @property
    def z(self):
        return self.val[2]

    @property
    def o(self):
        # TODO: distinguish between rotation and translation (vev 2 and vec3)
        return self.val[3]

    @x.setter
    def x(self, val):
        self.val[0] = val

    @y.setter
    def y(self, val):
        self.val[1] = val

    @z.setter
    def z(self, val):
        self.val[2] = val

    @o.setter
    def o(self, val):
        self.val[3] = val


class SFString:
    def __init__(self, val, add_quotes=False):
        if isinstance(val, str):
            self.val = val.strip('"')
        else:
            self.val = str(val)
        self.add_quotes = add_quotes

    def __add__(self, other):
        if isinstance(other, str):
            return SFString(self.no_quotes() + other)
        elif isinstance(other, SFString):
            return SFString(self.no_quotes() + other.no_quotes())

    def __str__(self):
        if self.add_quotes:
            return f'{self.val}'
        else:
            return f'"{self.val}"'

    def no_quotes(self):
        return f'{self.val}'  # .replace('.', '_')

    def yes_quotes(self):
        return f'"{self.val}"'  # .replace('.', '_')


class Cell:

    def __init__(self, x, y, translation, wheel_shape, cylinder_shape):
        self.wheel_shape = wheel_shape
        self.cylinder_shape = cylinder_shape

        self.translation = translation if isinstance(translation, SFVec) else SFVec(translation)

        self.name = SFString(f"cell_{x}_{y}")
        self.m1 = self.name + "_m1"
        self.m2 = self.name + "_m2"
        self.m3 = self.name + "_m3"

        self.joint1 = self.name + "_wheel_1"
        self.joint2 = self.name + "_wheel_2"
        self.joint3 = self.name + "_wheel_3"

        self.name_body = self.name + "_body"

        self._core_string = \
            f'''DEF {self.name.no_quotes()} Pose {{
    translation {self.translation}
    children [
      Solid {{
          children [
            Group {{
              children [
                CadShape {{
                  url [
                    {self.cylinder_shape.yes_quotes()}
                  ]
                }}
              ]
            }}
            DEF V1 Pose {{
              translation 0.04 0 0.1
              rotation 0 0 1 1.5707996938995747
              children [
                HingeJoint {{
                  jointParameters HingeJointParameters {{
                    axis 0 1 0
                  }}
                  device [
                    RotationalMotor {{
                      name {self.m1.yes_quotes()}
                    }}
                  ]
                  endPoint Solid {{
                    rotation -1 2.7476575974040475e-15 4.710270166978368e-16 1.5707993877991355
                    children [
                      Group {{
                        children [
                          DEF wheel_shape Shape {{
                            appearance PBRAppearance {{
                              transparency 1
                            }}
                            geometry Cylinder {{
                              height 0.025
                              radius 0.027
                            }}
                          }}
                          CadShape {{
                            url [
                              {self.wheel_shape.yes_quotes()}
                            ]
                          }}
                        ]
                      }}
                    ]
                    name {self.joint1.yes_quotes()}
                    boundingObject USE wheel_shape
                    physics Physics {{
                    }}
                  }}
                }}
              ]
            }}
            DEF V2 Pose {{
              translation -0.02 0.034 0.1
              rotation 0 0 1 -2.6179953071795863
              children [
                HingeJoint {{
                  jointParameters HingeJointParameters {{
                    axis 0 1 0
                  }}
                  device [
                    RotationalMotor {{
                      name {self.m2.yes_quotes()}
                    }}
                  ]
                  endPoint Solid {{
                    rotation -1 -8.635471348454006e-16 -7.850510172479671e-16 1.5707993877991429
                    children [
                      Group {{
                        children [
                          DEF wheel_shape Shape {{
                            appearance PBRAppearance {{
                              transparency 1
                            }}
                            geometry Cylinder {{
                              height 0.025
                              radius 0.027
                            }}
                          }}
                          CadShape {{
                            url [
                              {self.wheel_shape.yes_quotes()}
                            ]
                          }}
                        ]
                      }}
                    ]
                    name {self.joint2.yes_quotes()}
                    boundingObject USE wheel_shape
                    physics Physics {{
                    }}
                  }}
                }}
              ]
            }}
            DEF V3 Pose {{
              translation -0.02 -0.034 0.1
              rotation 0 0 1 -0.523595307179586
              children [
                HingeJoint {{
                  jointParameters HingeJointParameters {{
                    axis 0 1 0
                  }}
                  device [
                    RotationalMotor {{
                      name {self.m3.yes_quotes()}
                    }}
                  ]
                  endPoint Solid {{
                    rotation -1 1.5700900556594532e-16 8.635495306126993e-16 1.5707993877991393
                    children [
                      Group {{
                        children [
                          DEF wheel_shape Shape {{
                            appearance PBRAppearance {{
                              transparency 1
                            }}
                            geometry Cylinder {{
                              height 0.025
                              radius 0.027
                            }}
                          }}
                          CadShape {{
                            url [
                              {self.wheel_shape.yes_quotes()}
                            ]
                          }}
                        ]
                      }}
                    ]
                    name {self.joint3.yes_quotes()}
                    boundingObject USE wheel_shape
                    physics Physics {{
                    }}
                  }}
                }}
              ]
            }}
            DEF hexagon_shape Shape {{
              appearance PBRAppearance {{
                baseColor 1 0.333333 1
                transparency 1
              }}
              geometry Cylinder {{
                bottom FALSE
                height 0.2
                radius 0.09
                top FALSE
                subdivision 6
              }}
            }}
          ]
          name {self.name_body.yes_quotes()}
          boundingObject USE hexagon_shape
          physics Physics {{
          }}
        }}
    ]
    }}'''

    def __str__(self):
        return self._core_string


class CelluvoyeRobot:
    x_cell_dist = 0.174  # TODO: turn into dynamically modified straight from the gui.
    y_cell_dist = 0.152
    height = 0.101
    wheel_shape = SFString('Celluvoyer_wheel_0_1.dae')
    cylinder_shape = SFString('Celluvoyer_0_1.dae')

    def __init__(self, dimension_x, dimension_y, controller):
        self.translation_list = []
        self.cell_list = []
        self.dimension_x = dimension_x
        self.dimension_y = dimension_y
        self.controller = controller if isinstance(controller, SFString) else SFString(controller)
        # TODO: add other parameters like sync and stuff
        cells_str = self.create_cells()

        self._core_string = f'''DEF celluvoyer Robot {{
  children [
        {cells_str}
  ]
  name "main_robot"
  physics Physics {{
  }}
  locked TRUE
  controller {self.controller.yes_quotes()}
  synchronization FALSE
}}
'''

    def create_cells(self):
        t = -1
        for j in range(self.dimension_y):
            y = self.y_cell_dist * j
            t *= -1
            for i in range(self.dimension_x):
                if j % 2 == 0:
                    x = self.x_cell_dist * i
                else:
                    x = self.x_cell_dist * i + (t * self.x_cell_dist / 2)
                self.cell_list.append(Cell(i, j, SFVec([x, y, self.height]), self.wheel_shape, self.cylinder_shape))
        t = ''
        for c in self.cell_list:
            t += str(c)
        return t

    def __str__(self):
        return self._core_string


class Header:
    def __init__(self, filename, x, y, controller):
        self.filename = filename
        self.robot_object = CelluvoyeRobot(x, y, controller)
        body_str = str(self.robot_object)

        self.orientation = r"orientation 0.1446426463512726 -0.9891624130165184 0.025223511489070028 4.6692983323171"
        self.position = r"position 0.007286806676128004 0.20276337840156394 1.629154495736184"

        self.header = f"""#VRML_SIM R2023b utf8

EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/backgrounds/protos/TexturedBackground.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/backgrounds/protos/TexturedBackgroundLight.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023b/projects/objects/floors/protos/RectangleArena.proto"

WorldInfo {{
}}
Viewpoint {{
  {self.orientation}
  {self.position}
}}
TexturedBackground {{
}}
TexturedBackgroundLight {{
}}
RectangleArena {{
  floorSize 3 3
}}
{body_str} 
"""

    def __str__(self):
        return self.header


class Robot:
    def __init__(self, translation=None, rotation=None, description=None, supervisor=None, controller=None,
                 header=None, dimensions=None):

        if dimensions is None:
            dimensions = [1, 1]
        else:
            assert dimensions[0] >= 1 and dimensions[1] >= 1, "Both dimensions must be more than one at the same time"

        self.header = None
        self._translation = SFVec(translation)
        self._rotation = SFVec(rotation)
        self.description = description
        self.supervisor = supervisor
        self._controller = SFString(controller)

        self._dimensions = SFVec(dimensions)

        self._filename = "celluvoyer_table_0_3"
        self.read_filename = 'C:\\Users\\toupa\\Desktop\\ESE - S1\\PFE\\3D\\New folder\\protos\\celluvoyer0_1.proto'
        self.write_filename = f"C:\\Users\\toupa\\Desktop\\ESE - S1\\PFE\\3D\\New folder\\worlds\\{self.filename}.wbt"

        self.translation_list = []
        self.name_list = []
        self.name_list = []
        self._default_values = {}
        self.set_default_value()

    def __str__(self):
        return str(self.header)

    def update_data(self):
        self.header = Header(self.filename, *self.dimensions, self.controller)

    def create_file(self):
        self.update_data()
        self.write_filename = f"C:\\Users\\toupa\\Desktop\\ESE - S1\\PFE\\3D\\New folder\\worlds\\{self.filename}.wbt"
        print(f"file at: {self.write_filename}")
        with open(self.write_filename, 'w') as f:
            f.write(str(self))

    def start_controller(self, x, y, o):
        # todo:test later
        print(f'Starting controller with parameters {x}, {y}, {o}')
        self.webots_controller_exe_file = "\msys64\mingw64\bin\webots-controller.exe"
        self.controller_launcher_file_location = os.path.join(os.environ['WEBOTS_HOME'],
                                                              self.webots_controller_exe_file)
        self.options = f"--robot-name=cell_{x}_{y}"
        self.controller_file_location = r"C:\Users\toupa\Desktop\ESE - S1\PFE\3D\New folder\controllers\cell_controller_0_2\cell_controller_0_2.py"
        self.launch_controller_string = fr'{self.controller_launcher_file_location} {self.options} '
        self.backup_string = fr'"%WEBOTS_HOME%\msys64\mingw64\bin\webots-controller.exe" --robot-name=main_robot "C:\Users\toupa\Desktop\ESE - S1\PFE\3D\New folder\controllers\cell_controller_0_2\cell_controller_0_2.py"'
        print('Launching string: ', self.backup_string)
        print('cwd: ', os.getcwd())
        # fr'"%WEBOTS_HOME%\msys64\mingw64\bin\webots-controller.exe" --robot-name=main_robot "C:\Users\toupa\Desktop\ESE - S1\PFE\3D\New folder\controllers\cell_controller_0_2\cell_controller_0_2.py"'

        command = self.backup_string
        result = self.execute_command(command)
        print(result)
        print('Closing controller.')


    def set_default_value(self):
        self._default_values['filename'] = self.filename
        self._default_values['controller'] = '<extern>'
        self._default_values['location'] = {'x': self.translation.x, 'y': self.translation.y, 'z': self.translation.z}
        self._default_values['rotation'] = {'x': self.rotation.x, 'y': self.rotation.y, 'z': self.rotation.z,
                                            'o': self.rotation.o}
        self._default_values['dimensions'] = {'x': self.dimensions.x, 'y': self.dimensions.y}
        self._default_values['graphics'] = {'chassis': SFString('Celluvoyer_0_1.dae'),
                                            'wheel': SFString('Celluvoyer_wheel_0_1.dae')}
        self._default_values['cwd'] = r'C:\Users\toupa\Desktop\ESE - S1\PFE\Simulation_files'

        # TODO: save the state of the last inputted filename, pickle, or a sitting file or use native PyQt settings

    @property
    def default_values(self):
        return self._default_values

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, val):
        self._filename = SFString(val, add_quotes=True)

    @property
    def translation(self):
        return self._translation

    @translation.setter
    def translation(self, val):
        self._translation = SFVec(val)

    @property
    def controller(self):
        return str(self._controller)

    @controller.setter
    def controller(self, val):
        if type(val) is type(''):
            self._controller = SFString(val)
        else:
            self._controller = val

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, val):
        if type(val) is type(''):
            self._rotation = SFString(val)
        else:
            self._rotation = val

    @property
    def dimensions(self):
        return self._dimensions

    @dimensions.setter
    def dimensions(self, val):
        if isinstance(val, SFVec):
            self._dimensions = val
        else:
            self._dimensions = SFVec(val)


if __name__ == '__main__':
    r = Robot(translation=[0, 0, 0.1], dimensions=[5, 5], rotation=[0, 0, 1, 0], controller=r'<extern>')
    # r.create_file()
    # print(r)
    print(r.translation.x)
    r.translation.x = 10
    print(r.translation.x)
