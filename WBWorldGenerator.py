import os


class SFVec:
    # TODO: sfvec to sfvec assignment, same for SFString
    def __init__(self, val):
        self.val = val

    def __str__(self):
        self.val_str = ''
        if type(self.val) is type([]):
            for i in self.val:
                if type(i) is type(''):
                    self.val_str += f'"{i}"' + " "
                else:
                    self.val_str += str(i) + " "
            self.val_str += ''
        return self.val_str

    def __getitem__(self, item):
        assert type(item) is type(1)  # item is int
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


class SFVec:
    # TODO: sfvec to sfvec assignment, same for SFString
    def __init__(self, val):
        self.val = val

    def __str__(self):
        self.val_str = ''
        if type(self.val) is type([]):
            for i in self.val:
                if type(i) is type(''):
                    self.val_str += f'"{i}"' + " "
                else:
                    self.val_str += str(i) + " "
            self.val_str += ''
        return self.val_str

    def __getitem__(self, item):
        assert type(item) is type(1)  # item is int
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
    def __init__(self, val, istitle=False):
        if type(val) == type(''):
            self.val = val
        else:
            self.val = str(val)
        self.istitle = istitle

    def __str__(self):
        if self.istitle:
            return f'{self.val}'
        else:
            return f'"{self.val}"'

    def no_quotes(self):
        return f'{self.val}'.replace('.', '_')


class Celluvoyer:
    def __init__(self, translation, rotation, controller, filename, name):
        self.translation = translation
        self.rotation = rotation

        self._controller = controller
        self.name = name
        self._filename = filename
        self.wheel_graphic_path = r'"Celluvoyer_wheel_0_1.dae"'
        # r'"C:\Users\toupa\Desktop\ESE - S1\PFE\3D\New folder\worlds\Celluvoyer_wheel_0_1.dae"'
        self.chasis_graphic_path = r'"Celluvoyer_0_1.dae"'
        # r'"C:\Users\toupa\Desktop\ESE - S1\PFE\3D\New folder\worlds\Celluvoyer_0_1.dae"'
        # {self.name.no_quotes()}
        print(f"The controller inside cell: {self.controller}")

        self.core_string = f"""DEF celluvoyer Robot {{
      translation {self.translation}
      rotation {self.rotation}
      children [
        DEF V1 Pose {{
          translation 0.04 0 0.1
          rotation 0 0 1 1.5707996938995747
          children [
            HingeJoint {{
              jointParameters HingeJointParameters {{
                axis 0 1 0
              }}
              device [
                DEF m1 RotationalMotor {{
                  name "m1"
                }}
              ]
              endPoint Solid {{
                rotation -1 1.334576547310534e-15 -7.850450278297259e-17 1.5707993877991409
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
                      {self.wheel_graphic_path}
                    ]
                      }}
                    ]
                  }}
                ]
                name "solid(1)"
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
                DEF m2 RotationalMotor {{
                  name "m2"
                }}
              ]
              endPoint Solid {{
                rotation -1 -8.635495306126964e-16 -7.850450278297241e-16 1.5707993877991457
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
                      {self.wheel_graphic_path}
                    ]
                      }}
                    ]
                  }}
                ]
                name "solid(2)"
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
                DEF m3 RotationalMotor {{
                  name "m3"
                }}
              ]
              endPoint Solid {{
                rotation -1 -3.925225139148627e-16 3.1401801113189015e-16 1.5707993877991426
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
                      {self.wheel_graphic_path}
                    ]
                      }}
                    ]
                  }}
                ]
                boundingObject USE wheel_shape
                physics Physics {{
                }}
              }}
            }}
          ]
        }}
        Pose {{
          children [
            CadShape {{
              url [
            {self.chasis_graphic_path}
          ]
            }}
          ]
        }}
        DEF hexagon_shape Shape {{
          appearance PBRAppearance {{
          }}
          geometry Cylinder {{
            height 0.2
            radius 0.09
            top FALSE
            bottom FALSE
            subdivision 6
          }}
          castShadows TRUE
        }}
      ]
      name {self.name}
      boundingObject USE hexagon_shape
      physics Physics {{
      }}
      controller {self.controller}
    }}"""

    def __str__(self):
        return self.core_string

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, val):
        if type(val) == type(""):
            self._controller = SFString(val)
        else:
            self._controller = val


class Field:
    def __init__(self, field_name="field", type_name="", name="", value=None):
        self.field_name = field_name
        self.type_name = type_name
        self.name = name
        self.value = value
        self.value_str = ''
        if type(self.value) is type([]):
            for i in self.value:
                if type(i) is type(''):
                    self.value_str += f'"{i}"' + " "
                else:
                    self.value_str += str(i) + " "
            self.value_str += ''
        elif type(name) is type(''):
            self.value_str = f'"{name}"'

    def __str__(self):
        return f"{self.field_name} {self.type_name} {self.name} {self.value_str}\n"


class Header:
    def __init__(self, filename, fields=None, bodies=None):
        self.filename = filename
        self.fields = fields
        self.bodies = bodies
        if not self.fields: self.fields = []
        if not self.fields: self.bodies = []
        field_str = ''
        body_str = ''
        for i in self.fields:
            field_str += str(i)
        for i in self.bodies:
            body_str += str(i) + '\n'

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
    def __init__(self, translation=None, rotation=None, name=None, description=None, supervisor=None, controller=None,
                 header=None, fields=None,
                 cells=None, dimensions=None):

        if fields is None:
            fields = []
        if cells is None:
            cells = []
        if dimensions is None:
            dimensions = [1, 1]
        else:
            assert dimensions[0] >= 1 and dimensions[1] >= 1, "Both dimensions must be more than one at the same time"
        self._translation = SFVec(translation)
        self._rotation = SFVec(rotation)
        self.name = name
        self.description = description
        self.supervisor = supervisor
        self._controller = SFString(controller)

        self._dimensions = SFVec(dimensions)

        self._filename = "celluvoyer_table_0_3"
        self.read_filename = 'C:\\Users\\toupa\\Desktop\\ESE - S1\\PFE\\3D\\New folder\\protos\\celluvoyer0_1.proto'
        self.write_filename = f"C:\\Users\\toupa\\Desktop\\ESE - S1\\PFE\\3D\\New folder\\worlds\\{self.filename}.wbt"

        self.fields = fields
        self.cells = cells

        self.x_cell_dist = 0.174
        self.y_cell_dist = 0.152
        self.translation_list = []
        self.name_list = []

    def __str__(self):
        return str(self.header)

    def create_fields(self):
        self.fields = []
        self.fields.append(Field(field_name='field', type_name='SFVec3f', name='translation', value=[0, 0, 0.1]))
        self.fields.append(Field(field_name='field', type_name='SFRotation', name='rotation', value=[0, 0, 1, 0]))
        self.fields.append(
            Field(field_name='unconnectedField', type_name='SFVec2f', name='lines_columns_size', value=[2, 2]))

        self.fields.append(
            Field(field_name='field', type_name='SFString', name='controller', value="celluvoyer_controller_0_1"))
        self.fields.append(Field(field_name='field', type_name='MFString', name='wheel_graphic', value=[
            "C:/Users/toupa/Desktop/ESE - S1/PFE/3D/New folder/worlds/Celluvoyer_wheel_0_1.dae"]))
        self.fields.append(Field(field_name='field', type_name='MFString', name='chasis_graphic',
                                 value=["C:/Users/toupa/Desktop/ESE - S1/PFE/3D/New folder/worlds/Celluvoyer_0_1.dae"]))

    def create_cells(self, dimensions):
        self.cells = []
        # TODO: migrate create_cells and create fields inside Header
        t = -1
        # TODO: make sure you add global coordinates depending on where the first cell is
        for j in range(dimensions[1]):
            y = self.y_cell_dist * j
            t *= -1
            for i in range(dimensions[0]):
                if j % 2 == 0:
                    x = self.x_cell_dist * i
                else:
                    x = self.x_cell_dist * i + (t * self.x_cell_dist / 2)
                self.translation_list.append(SFVec([x, y, self.translation[2]]))
                self.name_list.append(f'cell_{i}_{j}')
        for cor in range(len(self.translation_list)):
            self.cells.append(Celluvoyer(self.translation_list[cor], self.rotation, self.controller,
                                         self.filename, SFString(self.name_list[cor])))

    def update_data(self):
        self.create_fields()
        self.create_cells(dimensions=self.dimensions)

        self.header = Header(self.filename, self.fields, self.cells)

    def create_file(self):
        self.update_data()
        self.write_filename = f"C:\\Users\\toupa\\Desktop\\ESE - S1\\PFE\\3D\\New folder\\worlds\\{self.filename}.wbt"
        print(f"Creating file at: {self.write_filename}")
        with open(self.write_filename, 'w') as f:
            f.write(str(self))

    def start_controller(self, x, y):
        # todo:test later
        self.webots_controller_exe_file = "\msys64\mingw64\bin\webots-controller.exe"
        self.controller_launcher_file_location = os.path.join(os.environ['WEBOTS_HOME'],
                                                              self.webots_controller_exe_file)
        self.options = f"--robot-name=cell_{x}_{y}"
        self.controller_file_location = r"C:\Users\toupa\Desktop\ESE - S1\PFE\3D\New folder\controllers\cell_controller_0_2\cell_controller_0_2.py"
        self.launch_controller_string = fr'{self.controller_launcher_file_location} {self.options} '
        # fr'"%WEBOTS_HOME%\msys64\mingw64\bin\webots-controller.exe" --robot-name=cell_1_1 "C:\Users\toupa\Desktop\ESE - S1\PFE\3D\New folder\controllers\cell_controller_0_2\cell_controller_0_2.py"'

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, val):
        self._filename = SFString(val, istitle=True)

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
        self._rotation = SFString(val)

    @property
    def dimensions(self):
        return self._dimensions

    @dimensions.setter
    def dimensions(self, val):
        self._dimensions = SFVec(val)


if __name__ == '__main__':
    r = Robot(translation=[0, 0, 0.1], dimensions=[5, 5], rotation=[0, 0, 1, 0], controller=r'<extern>')
    # r.create_file()
    # print(r)
    print(r.translation.x)
    r.translation.x = 10
    print(r.translation.x)
